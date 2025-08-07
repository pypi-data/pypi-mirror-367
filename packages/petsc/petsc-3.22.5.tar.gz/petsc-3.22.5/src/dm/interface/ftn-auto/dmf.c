#include "petscsys.h"
#include "petscfix.h"
#include "petsc/private/fortranimpl.h"
/* dm.c */
/* Fortran interface file */

/*
* This file was generated automatically by bfort from the C source
* file.  
 */

#ifdef PETSC_USE_POINTER_CONVERSION
#if defined(__cplusplus)
extern "C" { 
#endif 
extern void *PetscToPointer(void*);
extern int PetscFromPointer(void *);
extern void PetscRmPointer(void*);
#if defined(__cplusplus)
} 
#endif 

#else

#define PetscToPointer(a) (a ? *(PetscFortranAddr *)(a) : 0)
#define PetscFromPointer(a) (PetscFortranAddr)(a)
#define PetscRmPointer(a)
#endif

#include "petscdm.h"
#include "petscdmlabel.h"
#include "petscds.h"
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define dmcreate_ DMCREATE
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define dmcreate_ dmcreate
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define dmclone_ DMCLONE
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define dmclone_ dmclone
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define dmsetvectype_ DMSETVECTYPE
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define dmsetvectype_ dmsetvectype
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define dmgetvectype_ DMGETVECTYPE
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define dmgetvectype_ dmgetvectype
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define vecgetdm_ VECGETDM
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define vecgetdm_ vecgetdm
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define vecsetdm_ VECSETDM
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define vecsetdm_ vecsetdm
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define dmsetiscoloringtype_ DMSETISCOLORINGTYPE
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define dmsetiscoloringtype_ dmsetiscoloringtype
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define dmgetiscoloringtype_ DMGETISCOLORINGTYPE
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define dmgetiscoloringtype_ dmgetiscoloringtype
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define dmsetmattype_ DMSETMATTYPE
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define dmsetmattype_ dmsetmattype
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define dmgetmattype_ DMGETMATTYPE
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define dmgetmattype_ dmgetmattype
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define matgetdm_ MATGETDM
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define matgetdm_ matgetdm
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define matsetdm_ MATSETDM
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define matsetdm_ matsetdm
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define dmsetoptionsprefix_ DMSETOPTIONSPREFIX
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define dmsetoptionsprefix_ dmsetoptionsprefix
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define dmappendoptionsprefix_ DMAPPENDOPTIONSPREFIX
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define dmappendoptionsprefix_ dmappendoptionsprefix
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define dmgetoptionsprefix_ DMGETOPTIONSPREFIX
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define dmgetoptionsprefix_ dmgetoptionsprefix
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define dmdestroy_ DMDESTROY
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define dmdestroy_ dmdestroy
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define dmsetup_ DMSETUP
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define dmsetup_ dmsetup
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define dmsetfromoptions_ DMSETFROMOPTIONS
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define dmsetfromoptions_ dmsetfromoptions
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define dmviewfromoptions_ DMVIEWFROMOPTIONS
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define dmviewfromoptions_ dmviewfromoptions
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define dmview_ DMVIEW
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define dmview_ dmview
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define dmcreateglobalvector_ DMCREATEGLOBALVECTOR
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define dmcreateglobalvector_ dmcreateglobalvector
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define dmcreatelocalvector_ DMCREATELOCALVECTOR
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define dmcreatelocalvector_ dmcreatelocalvector
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define dmgetlocaltoglobalmapping_ DMGETLOCALTOGLOBALMAPPING
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define dmgetlocaltoglobalmapping_ dmgetlocaltoglobalmapping
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define dmgetblocksize_ DMGETBLOCKSIZE
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define dmgetblocksize_ dmgetblocksize
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define dmcreateinterpolation_ DMCREATEINTERPOLATION
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define dmcreateinterpolation_ dmcreateinterpolation
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define dmcreateinterpolationscale_ DMCREATEINTERPOLATIONSCALE
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define dmcreateinterpolationscale_ dmcreateinterpolationscale
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define dmcreaterestriction_ DMCREATERESTRICTION
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define dmcreaterestriction_ dmcreaterestriction
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define dmcreateinjection_ DMCREATEINJECTION
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define dmcreateinjection_ dmcreateinjection
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define dmcreatemassmatrix_ DMCREATEMASSMATRIX
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define dmcreatemassmatrix_ dmcreatemassmatrix
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define dmcreatemassmatrixlumped_ DMCREATEMASSMATRIXLUMPED
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define dmcreatemassmatrixlumped_ dmcreatemassmatrixlumped
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define dmcreatecoloring_ DMCREATECOLORING
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define dmcreatecoloring_ dmcreatecoloring
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define dmcreatematrix_ DMCREATEMATRIX
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define dmcreatematrix_ dmcreatematrix
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define dmsetmatrixpreallocateskip_ DMSETMATRIXPREALLOCATESKIP
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define dmsetmatrixpreallocateskip_ dmsetmatrixpreallocateskip
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define dmsetmatrixpreallocateonly_ DMSETMATRIXPREALLOCATEONLY
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define dmsetmatrixpreallocateonly_ dmsetmatrixpreallocateonly
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define dmsetmatrixstructureonly_ DMSETMATRIXSTRUCTUREONLY
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define dmsetmatrixstructureonly_ dmsetmatrixstructureonly
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define dmsetblockingtype_ DMSETBLOCKINGTYPE
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define dmsetblockingtype_ dmsetblockingtype
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define dmgetblockingtype_ DMGETBLOCKINGTYPE
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define dmgetblockingtype_ dmgetblockingtype
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define dmcreatesubdm_ DMCREATESUBDM
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define dmcreatesubdm_ dmcreatesubdm
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define dmrefine_ DMREFINE
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define dmrefine_ dmrefine
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define dminterpolate_ DMINTERPOLATE
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define dminterpolate_ dminterpolate
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define dminterpolatesolution_ DMINTERPOLATESOLUTION
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define dminterpolatesolution_ dminterpolatesolution
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define dmgetrefinelevel_ DMGETREFINELEVEL
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define dmgetrefinelevel_ dmgetrefinelevel
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define dmsetrefinelevel_ DMSETREFINELEVEL
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define dmsetrefinelevel_ dmsetrefinelevel
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define dmextrude_ DMEXTRUDE
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define dmextrude_ dmextrude
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define dmhasbasistransform_ DMHASBASISTRANSFORM
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define dmhasbasistransform_ dmhasbasistransform
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define dmglobaltolocal_ DMGLOBALTOLOCAL
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define dmglobaltolocal_ dmglobaltolocal
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define dmglobaltolocalbegin_ DMGLOBALTOLOCALBEGIN
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define dmglobaltolocalbegin_ dmglobaltolocalbegin
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define dmglobaltolocalend_ DMGLOBALTOLOCALEND
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define dmglobaltolocalend_ dmglobaltolocalend
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define dmlocaltoglobal_ DMLOCALTOGLOBAL
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define dmlocaltoglobal_ dmlocaltoglobal
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define dmlocaltoglobalbegin_ DMLOCALTOGLOBALBEGIN
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define dmlocaltoglobalbegin_ dmlocaltoglobalbegin
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define dmlocaltoglobalend_ DMLOCALTOGLOBALEND
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define dmlocaltoglobalend_ dmlocaltoglobalend
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define dmlocaltolocalbegin_ DMLOCALTOLOCALBEGIN
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define dmlocaltolocalbegin_ dmlocaltolocalbegin
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define dmlocaltolocalend_ DMLOCALTOLOCALEND
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define dmlocaltolocalend_ dmlocaltolocalend
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define dmcoarsen_ DMCOARSEN
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define dmcoarsen_ dmcoarsen
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define dmrestrict_ DMRESTRICT
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define dmrestrict_ dmrestrict
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define dmsubdomainrestrict_ DMSUBDOMAINRESTRICT
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define dmsubdomainrestrict_ dmsubdomainrestrict
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define dmgetcoarsenlevel_ DMGETCOARSENLEVEL
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define dmgetcoarsenlevel_ dmgetcoarsenlevel
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define dmsetcoarsenlevel_ DMSETCOARSENLEVEL
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define dmsetcoarsenlevel_ dmsetcoarsenlevel
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define dmrefinehierarchy_ DMREFINEHIERARCHY
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define dmrefinehierarchy_ dmrefinehierarchy
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define dmcoarsenhierarchy_ DMCOARSENHIERARCHY
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define dmcoarsenhierarchy_ dmcoarsenhierarchy
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define dmsetapplicationcontext_ DMSETAPPLICATIONCONTEXT
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define dmsetapplicationcontext_ dmsetapplicationcontext
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define dmgetapplicationcontext_ DMGETAPPLICATIONCONTEXT
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define dmgetapplicationcontext_ dmgetapplicationcontext
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define dmhasvariablebounds_ DMHASVARIABLEBOUNDS
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define dmhasvariablebounds_ dmhasvariablebounds
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define dmcomputevariablebounds_ DMCOMPUTEVARIABLEBOUNDS
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define dmcomputevariablebounds_ dmcomputevariablebounds
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define dmhascoloring_ DMHASCOLORING
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define dmhascoloring_ dmhascoloring
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define dmhascreaterestriction_ DMHASCREATERESTRICTION
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define dmhascreaterestriction_ dmhascreaterestriction
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define dmhascreateinjection_ DMHASCREATEINJECTION
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define dmhascreateinjection_ dmhascreateinjection
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define dmsettype_ DMSETTYPE
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define dmsettype_ dmsettype
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define dmgettype_ DMGETTYPE
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define dmgettype_ dmgettype
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define dmconvert_ DMCONVERT
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define dmconvert_ dmconvert
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define dmload_ DMLOAD
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define dmload_ dmload
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define dmgetsection_ DMGETSECTION
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define dmgetsection_ dmgetsection
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define dmgetlocalsection_ DMGETLOCALSECTION
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define dmgetlocalsection_ dmgetlocalsection
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define dmsetsection_ DMSETSECTION
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define dmsetsection_ dmsetsection
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define dmsetlocalsection_ DMSETLOCALSECTION
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define dmsetlocalsection_ dmsetlocalsection
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define dmgetdefaultconstraints_ DMGETDEFAULTCONSTRAINTS
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define dmgetdefaultconstraints_ dmgetdefaultconstraints
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define dmsetdefaultconstraints_ DMSETDEFAULTCONSTRAINTS
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define dmsetdefaultconstraints_ dmsetdefaultconstraints
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define dmgetglobalsection_ DMGETGLOBALSECTION
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define dmgetglobalsection_ dmgetglobalsection
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define dmsetglobalsection_ DMSETGLOBALSECTION
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define dmsetglobalsection_ dmsetglobalsection
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define dmgetsectionsf_ DMGETSECTIONSF
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define dmgetsectionsf_ dmgetsectionsf
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define dmsetsectionsf_ DMSETSECTIONSF
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define dmsetsectionsf_ dmsetsectionsf
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define dmcreatesectionsf_ DMCREATESECTIONSF
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define dmcreatesectionsf_ dmcreatesectionsf
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define dmgetpointsf_ DMGETPOINTSF
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define dmgetpointsf_ dmgetpointsf
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define dmsetpointsf_ DMSETPOINTSF
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define dmsetpointsf_ dmsetpointsf
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define dmgetnaturalsf_ DMGETNATURALSF
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define dmgetnaturalsf_ dmgetnaturalsf
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define dmsetnaturalsf_ DMSETNATURALSF
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define dmsetnaturalsf_ dmsetnaturalsf
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define dmclearfields_ DMCLEARFIELDS
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define dmclearfields_ dmclearfields
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define dmgetnumfields_ DMGETNUMFIELDS
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define dmgetnumfields_ dmgetnumfields
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define dmsetnumfields_ DMSETNUMFIELDS
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define dmsetnumfields_ dmsetnumfields
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define dmgetfield_ DMGETFIELD
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define dmgetfield_ dmgetfield
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define dmsetfield_ DMSETFIELD
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define dmsetfield_ dmsetfield
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define dmaddfield_ DMADDFIELD
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define dmaddfield_ dmaddfield
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define dmsetfieldavoidtensor_ DMSETFIELDAVOIDTENSOR
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define dmsetfieldavoidtensor_ dmsetfieldavoidtensor
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define dmgetfieldavoidtensor_ DMGETFIELDAVOIDTENSOR
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define dmgetfieldavoidtensor_ dmgetfieldavoidtensor
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define dmcopyfields_ DMCOPYFIELDS
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define dmcopyfields_ dmcopyfields
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define dmgetadjacency_ DMGETADJACENCY
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define dmgetadjacency_ dmgetadjacency
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define dmsetadjacency_ DMSETADJACENCY
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define dmsetadjacency_ dmsetadjacency
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define dmgetbasicadjacency_ DMGETBASICADJACENCY
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define dmgetbasicadjacency_ dmgetbasicadjacency
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define dmsetbasicadjacency_ DMSETBASICADJACENCY
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define dmsetbasicadjacency_ dmsetbasicadjacency
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define dmgetnumds_ DMGETNUMDS
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define dmgetnumds_ dmgetnumds
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define dmcleards_ DMCLEARDS
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define dmcleards_ dmcleards
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define dmgetds_ DMGETDS
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define dmgetds_ dmgetds
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define dmgetcellds_ DMGETCELLDS
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define dmgetcellds_ dmgetcellds
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define dmgetregionds_ DMGETREGIONDS
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define dmgetregionds_ dmgetregionds
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define dmsetregionds_ DMSETREGIONDS
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define dmsetregionds_ dmsetregionds
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define dmgetregionnumds_ DMGETREGIONNUMDS
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define dmgetregionnumds_ dmgetregionnumds
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define dmsetregionnumds_ DMSETREGIONNUMDS
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define dmsetregionnumds_ dmsetregionnumds
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define dmfindregionnum_ DMFINDREGIONNUM
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define dmfindregionnum_ dmfindregionnum
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define dmcreatefedefault_ DMCREATEFEDEFAULT
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define dmcreatefedefault_ dmcreatefedefault
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define dmcreateds_ DMCREATEDS
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define dmcreateds_ dmcreateds
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define dmusetensororder_ DMUSETENSORORDER
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define dmusetensororder_ dmusetensororder
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define dmcomputeexactsolution_ DMCOMPUTEEXACTSOLUTION
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define dmcomputeexactsolution_ dmcomputeexactsolution
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define dmcopyds_ DMCOPYDS
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define dmcopyds_ dmcopyds
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define dmcopydisc_ DMCOPYDISC
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define dmcopydisc_ dmcopydisc
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define dmgetdimension_ DMGETDIMENSION
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define dmgetdimension_ dmgetdimension
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define dmsetdimension_ DMSETDIMENSION
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define dmsetdimension_ dmsetdimension
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define dmgetdimpoints_ DMGETDIMPOINTS
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define dmgetdimpoints_ dmgetdimpoints
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define dmgetoutputdm_ DMGETOUTPUTDM
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define dmgetoutputdm_ dmgetoutputdm
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define dmgetoutputsequencenumber_ DMGETOUTPUTSEQUENCENUMBER
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define dmgetoutputsequencenumber_ dmgetoutputsequencenumber
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define dmsetoutputsequencenumber_ DMSETOUTPUTSEQUENCENUMBER
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define dmsetoutputsequencenumber_ dmsetoutputsequencenumber
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define dmoutputsequenceload_ DMOUTPUTSEQUENCELOAD
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define dmoutputsequenceload_ dmoutputsequenceload
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define dmgetoutputsequencelength_ DMGETOUTPUTSEQUENCELENGTH
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define dmgetoutputsequencelength_ dmgetoutputsequencelength
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define dmgetusenatural_ DMGETUSENATURAL
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define dmgetusenatural_ dmgetusenatural
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define dmsetusenatural_ DMSETUSENATURAL
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define dmsetusenatural_ dmsetusenatural
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define dmcreatelabel_ DMCREATELABEL
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define dmcreatelabel_ dmcreatelabel
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define dmcreatelabelatindex_ DMCREATELABELATINDEX
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define dmcreatelabelatindex_ dmcreatelabelatindex
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define dmgetlabelvalue_ DMGETLABELVALUE
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define dmgetlabelvalue_ dmgetlabelvalue
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define dmsetlabelvalue_ DMSETLABELVALUE
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define dmsetlabelvalue_ dmsetlabelvalue
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define dmclearlabelvalue_ DMCLEARLABELVALUE
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define dmclearlabelvalue_ dmclearlabelvalue
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define dmgetlabelsize_ DMGETLABELSIZE
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define dmgetlabelsize_ dmgetlabelsize
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define dmgetlabelidis_ DMGETLABELIDIS
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define dmgetlabelidis_ dmgetlabelidis
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define dmgetstratumsize_ DMGETSTRATUMSIZE
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define dmgetstratumsize_ dmgetstratumsize
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define dmgetstratumis_ DMGETSTRATUMIS
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define dmgetstratumis_ dmgetstratumis
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define dmsetstratumis_ DMSETSTRATUMIS
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define dmsetstratumis_ dmsetstratumis
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define dmclearlabelstratum_ DMCLEARLABELSTRATUM
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define dmclearlabelstratum_ dmclearlabelstratum
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define dmgetnumlabels_ DMGETNUMLABELS
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define dmgetnumlabels_ dmgetnumlabels
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define dmgetlabelname_ DMGETLABELNAME
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define dmgetlabelname_ dmgetlabelname
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define dmhaslabel_ DMHASLABEL
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define dmhaslabel_ dmhaslabel
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define dmgetlabel_ DMGETLABEL
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define dmgetlabel_ dmgetlabel
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define dmgetlabelbynum_ DMGETLABELBYNUM
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define dmgetlabelbynum_ dmgetlabelbynum
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define dmaddlabel_ DMADDLABEL
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define dmaddlabel_ dmaddlabel
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define dmsetlabel_ DMSETLABEL
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define dmsetlabel_ dmsetlabel
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define dmremovelabel_ DMREMOVELABEL
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define dmremovelabel_ dmremovelabel
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define dmremovelabelbyself_ DMREMOVELABELBYSELF
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define dmremovelabelbyself_ dmremovelabelbyself
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define dmgetlabeloutput_ DMGETLABELOUTPUT
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define dmgetlabeloutput_ dmgetlabeloutput
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define dmsetlabeloutput_ DMSETLABELOUTPUT
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define dmsetlabeloutput_ dmsetlabeloutput
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define dmcopylabels_ DMCOPYLABELS
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define dmcopylabels_ dmcopylabels
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define dmgetcoarsedm_ DMGETCOARSEDM
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define dmgetcoarsedm_ dmgetcoarsedm
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define dmsetcoarsedm_ DMSETCOARSEDM
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define dmsetcoarsedm_ dmsetcoarsedm
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define dmgetfinedm_ DMGETFINEDM
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define dmgetfinedm_ dmgetfinedm
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define dmsetfinedm_ DMSETFINEDM
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define dmsetfinedm_ dmsetfinedm
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define matfdcoloringusedm_ MATFDCOLORINGUSEDM
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define matfdcoloringusedm_ matfdcoloringusedm
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define dmgetcompatibility_ DMGETCOMPATIBILITY
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define dmgetcompatibility_ dmgetcompatibility
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define dmmonitorcancel_ DMMONITORCANCEL
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define dmmonitorcancel_ dmmonitorcancel
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define dmmonitor_ DMMONITOR
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define dmmonitor_ dmmonitor
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define dmcomputeerror_ DMCOMPUTEERROR
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define dmcomputeerror_ dmcomputeerror
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define dmgetnumauxiliaryvec_ DMGETNUMAUXILIARYVEC
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define dmgetnumauxiliaryvec_ dmgetnumauxiliaryvec
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define dmgetauxiliaryvec_ DMGETAUXILIARYVEC
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define dmgetauxiliaryvec_ dmgetauxiliaryvec
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define dmsetauxiliaryvec_ DMSETAUXILIARYVEC
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define dmsetauxiliaryvec_ dmsetauxiliaryvec
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define dmgetauxiliarylabels_ DMGETAUXILIARYLABELS
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define dmgetauxiliarylabels_ dmgetauxiliarylabels
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define dmcopyauxiliaryvec_ DMCOPYAUXILIARYVEC
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define dmcopyauxiliaryvec_ dmcopyauxiliaryvec
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define dmclearauxiliaryvec_ DMCLEARAUXILIARYVEC
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define dmclearauxiliaryvec_ dmclearauxiliaryvec
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define dmpolytopematchorientation_ DMPOLYTOPEMATCHORIENTATION
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define dmpolytopematchorientation_ dmpolytopematchorientation
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define dmpolytopegetorientation_ DMPOLYTOPEGETORIENTATION
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define dmpolytopegetorientation_ dmpolytopegetorientation
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define dmpolytopematchvertexorientation_ DMPOLYTOPEMATCHVERTEXORIENTATION
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define dmpolytopematchvertexorientation_ dmpolytopematchvertexorientation
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define dmpolytopegetvertexorientation_ DMPOLYTOPEGETVERTEXORIENTATION
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define dmpolytopegetvertexorientation_ dmpolytopegetvertexorientation
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define dmpolytopeincelltest_ DMPOLYTOPEINCELLTEST
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define dmpolytopeincelltest_ dmpolytopeincelltest
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define dmreordersectionsetdefault_ DMREORDERSECTIONSETDEFAULT
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define dmreordersectionsetdefault_ dmreordersectionsetdefault
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define dmreordersectiongetdefault_ DMREORDERSECTIONGETDEFAULT
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define dmreordersectiongetdefault_ dmreordersectiongetdefault
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define dmreordersectionsettype_ DMREORDERSECTIONSETTYPE
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define dmreordersectionsettype_ dmreordersectionsettype
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define dmreordersectiongettype_ DMREORDERSECTIONGETTYPE
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define dmreordersectiongettype_ dmreordersectiongettype
#endif
/* Provide declarations for malloc/free if needed for strings */
#include <stdlib.h>


/* Definitions of Fortran Wrapper routines */
#if defined(__cplusplus)
extern "C" {
#endif
PETSC_EXTERN void  dmcreate_(MPI_Fint * comm,DM *dm, int *ierr)
{
PETSC_FORTRAN_OBJECT_CREATE(dm);
 PetscBool dm_null = !*(void**) dm ? PETSC_TRUE : PETSC_FALSE;
CHKFORTRANNULLOBJECT(dm);
*ierr = DMCreate(
	MPI_Comm_f2c(*(comm)),dm);
// if C routine nullifed the object, we must set to to -2 to indicate null set in Fortran
if (! dm_null && !*(void**) dm) * (void **) dm = (void *)-2;
}
PETSC_EXTERN void  dmclone_(DM dm,DM *newdm, int *ierr)
{
CHKFORTRANNULLOBJECT(dm);
PetscBool newdm_null = !*(void**) newdm ? PETSC_TRUE : PETSC_FALSE;
CHKFORTRANNULLOBJECT(newdm);
*ierr = DMClone(
	(DM)PetscToPointer((dm) ),newdm);
// if C routine nullifed the object, we must set to to -2 to indicate null set in Fortran
if (! newdm_null && !*(void**) newdm) * (void **) newdm = (void *)-2;
}
PETSC_EXTERN void  dmsetvectype_(DM dm,char *ctype, int *ierr, PETSC_FORTRAN_CHARLEN_T cl0)
{
  char *_cltmp0 = PETSC_NULLPTR;
CHKFORTRANNULLOBJECT(dm);
/* insert Fortran-to-C conversion for ctype */
  FIXCHAR(ctype,cl0,_cltmp0);
*ierr = DMSetVecType(
	(DM)PetscToPointer((dm) ),_cltmp0);
  FREECHAR(ctype,_cltmp0);
}
PETSC_EXTERN void  dmgetvectype_(DM da,char *ctype, int *ierr, PETSC_FORTRAN_CHARLEN_T cl0)
{
  char *_cltmp0 = PETSC_NULLPTR;
CHKFORTRANNULLOBJECT(da);
*ierr = DMGetVecType(
	(DM)PetscToPointer((da) ),(const char **)&_cltmp0);
/* insert C-to-Fortran conversion for ctype */
*ierr = PetscStrncpy(ctype, _cltmp0, cl0);
                        if (*ierr) return;
                        FIXRETURNCHAR(PETSC_TRUE, ctype, cl0);
}
PETSC_EXTERN void  vecgetdm_(Vec v,DM *dm, int *ierr)
{
CHKFORTRANNULLOBJECT(v);
PetscBool dm_null = !*(void**) dm ? PETSC_TRUE : PETSC_FALSE;
CHKFORTRANNULLOBJECT(dm);
*ierr = VecGetDM(
	(Vec)PetscToPointer((v) ),dm);
// if C routine nullifed the object, we must set to to -2 to indicate null set in Fortran
if (! dm_null && !*(void**) dm) * (void **) dm = (void *)-2;
}
PETSC_EXTERN void  vecsetdm_(Vec v,DM dm, int *ierr)
{
CHKFORTRANNULLOBJECT(v);
CHKFORTRANNULLOBJECT(dm);
*ierr = VecSetDM(
	(Vec)PetscToPointer((v) ),
	(DM)PetscToPointer((dm) ));
}
PETSC_EXTERN void  dmsetiscoloringtype_(DM dm,ISColoringType *ctype, int *ierr)
{
CHKFORTRANNULLOBJECT(dm);
*ierr = DMSetISColoringType(
	(DM)PetscToPointer((dm) ),*ctype);
}
PETSC_EXTERN void  dmgetiscoloringtype_(DM dm,ISColoringType *ctype, int *ierr)
{
CHKFORTRANNULLOBJECT(dm);
*ierr = DMGetISColoringType(
	(DM)PetscToPointer((dm) ),ctype);
}
PETSC_EXTERN void  dmsetmattype_(DM dm,char *ctype, int *ierr, PETSC_FORTRAN_CHARLEN_T cl0)
{
  char *_cltmp0 = PETSC_NULLPTR;
CHKFORTRANNULLOBJECT(dm);
/* insert Fortran-to-C conversion for ctype */
  FIXCHAR(ctype,cl0,_cltmp0);
*ierr = DMSetMatType(
	(DM)PetscToPointer((dm) ),_cltmp0);
  FREECHAR(ctype,_cltmp0);
}
PETSC_EXTERN void  dmgetmattype_(DM dm,char *ctype, int *ierr, PETSC_FORTRAN_CHARLEN_T cl0)
{
  char *_cltmp0 = PETSC_NULLPTR;
CHKFORTRANNULLOBJECT(dm);
*ierr = DMGetMatType(
	(DM)PetscToPointer((dm) ),(const char **)&_cltmp0);
/* insert C-to-Fortran conversion for ctype */
*ierr = PetscStrncpy(ctype, _cltmp0, cl0);
                        if (*ierr) return;
                        FIXRETURNCHAR(PETSC_TRUE, ctype, cl0);
}
PETSC_EXTERN void  matgetdm_(Mat A,DM *dm, int *ierr)
{
CHKFORTRANNULLOBJECT(A);
PetscBool dm_null = !*(void**) dm ? PETSC_TRUE : PETSC_FALSE;
CHKFORTRANNULLOBJECT(dm);
*ierr = MatGetDM(
	(Mat)PetscToPointer((A) ),dm);
// if C routine nullifed the object, we must set to to -2 to indicate null set in Fortran
if (! dm_null && !*(void**) dm) * (void **) dm = (void *)-2;
}
PETSC_EXTERN void  matsetdm_(Mat A,DM dm, int *ierr)
{
CHKFORTRANNULLOBJECT(A);
CHKFORTRANNULLOBJECT(dm);
*ierr = MatSetDM(
	(Mat)PetscToPointer((A) ),
	(DM)PetscToPointer((dm) ));
}
PETSC_EXTERN void  dmsetoptionsprefix_(DM dm, char prefix[], int *ierr, PETSC_FORTRAN_CHARLEN_T cl0)
{
  char *_cltmp0 = PETSC_NULLPTR;
CHKFORTRANNULLOBJECT(dm);
/* insert Fortran-to-C conversion for prefix */
  FIXCHAR(prefix,cl0,_cltmp0);
*ierr = DMSetOptionsPrefix(
	(DM)PetscToPointer((dm) ),_cltmp0);
  FREECHAR(prefix,_cltmp0);
}
PETSC_EXTERN void  dmappendoptionsprefix_(DM dm, char prefix[], int *ierr, PETSC_FORTRAN_CHARLEN_T cl0)
{
  char *_cltmp0 = PETSC_NULLPTR;
CHKFORTRANNULLOBJECT(dm);
/* insert Fortran-to-C conversion for prefix */
  FIXCHAR(prefix,cl0,_cltmp0);
*ierr = DMAppendOptionsPrefix(
	(DM)PetscToPointer((dm) ),_cltmp0);
  FREECHAR(prefix,_cltmp0);
}
PETSC_EXTERN void  dmgetoptionsprefix_(DM dm, char *prefix, int *ierr, PETSC_FORTRAN_CHARLEN_T cl0)
{
  char *_cltmp0 = PETSC_NULLPTR;
CHKFORTRANNULLOBJECT(dm);
*ierr = DMGetOptionsPrefix(
	(DM)PetscToPointer((dm) ),(const char **)&_cltmp0);
/* insert C-to-Fortran conversion for prefix */
*ierr = PetscStrncpy(prefix, _cltmp0, cl0);
                        if (*ierr) return;
                        FIXRETURNCHAR(PETSC_TRUE, prefix, cl0);
}
PETSC_EXTERN void  dmdestroy_(DM *dm, int *ierr)
{
PETSC_FORTRAN_OBJECT_F_DESTROYED_TO_C_NULL(dm);
 PetscBool dm_null = !*(void**) dm ? PETSC_TRUE : PETSC_FALSE;
CHKFORTRANNULLOBJECT(dm);
*ierr = DMDestroy(dm);
// if C routine nullifed the object, we must set to to -2 to indicate null set in Fortran
if (! dm_null && !*(void**) dm) * (void **) dm = (void *)-2;
if (*ierr) return;
PETSC_FORTRAN_OBJECT_C_NULL_TO_F_DESTROYED(dm);
 }
PETSC_EXTERN void  dmsetup_(DM dm, int *ierr)
{
CHKFORTRANNULLOBJECT(dm);
*ierr = DMSetUp(
	(DM)PetscToPointer((dm) ));
}
PETSC_EXTERN void  dmsetfromoptions_(DM dm, int *ierr)
{
CHKFORTRANNULLOBJECT(dm);
*ierr = DMSetFromOptions(
	(DM)PetscToPointer((dm) ));
}
PETSC_EXTERN void  dmviewfromoptions_(DM dm,PetscObject obj, char name[], int *ierr, PETSC_FORTRAN_CHARLEN_T cl0)
{
  char *_cltmp0 = PETSC_NULLPTR;
CHKFORTRANNULLOBJECT(dm);
CHKFORTRANNULLOBJECT(obj);
/* insert Fortran-to-C conversion for name */
  FIXCHAR(name,cl0,_cltmp0);
*ierr = DMViewFromOptions(
	(DM)PetscToPointer((dm) ),
	(PetscObject)PetscToPointer((obj) ),_cltmp0);
  FREECHAR(name,_cltmp0);
}
PETSC_EXTERN void  dmview_(DM dm,PetscViewer v, int *ierr)
{
CHKFORTRANNULLOBJECT(dm);
CHKFORTRANNULLOBJECT(v);
*ierr = DMView(
	(DM)PetscToPointer((dm) ),PetscPatchDefaultViewers((PetscViewer*)v));
}
PETSC_EXTERN void  dmcreateglobalvector_(DM dm,Vec *vec, int *ierr)
{
CHKFORTRANNULLOBJECT(dm);
PetscBool vec_null = !*(void**) vec ? PETSC_TRUE : PETSC_FALSE;
CHKFORTRANNULLOBJECT(vec);
*ierr = DMCreateGlobalVector(
	(DM)PetscToPointer((dm) ),vec);
// if C routine nullifed the object, we must set to to -2 to indicate null set in Fortran
if (! vec_null && !*(void**) vec) * (void **) vec = (void *)-2;
}
PETSC_EXTERN void  dmcreatelocalvector_(DM dm,Vec *vec, int *ierr)
{
CHKFORTRANNULLOBJECT(dm);
PetscBool vec_null = !*(void**) vec ? PETSC_TRUE : PETSC_FALSE;
CHKFORTRANNULLOBJECT(vec);
*ierr = DMCreateLocalVector(
	(DM)PetscToPointer((dm) ),vec);
// if C routine nullifed the object, we must set to to -2 to indicate null set in Fortran
if (! vec_null && !*(void**) vec) * (void **) vec = (void *)-2;
}
PETSC_EXTERN void  dmgetlocaltoglobalmapping_(DM dm,ISLocalToGlobalMapping *ltog, int *ierr)
{
CHKFORTRANNULLOBJECT(dm);
PetscBool ltog_null = !*(void**) ltog ? PETSC_TRUE : PETSC_FALSE;
CHKFORTRANNULLOBJECT(ltog);
*ierr = DMGetLocalToGlobalMapping(
	(DM)PetscToPointer((dm) ),ltog);
// if C routine nullifed the object, we must set to to -2 to indicate null set in Fortran
if (! ltog_null && !*(void**) ltog) * (void **) ltog = (void *)-2;
}
PETSC_EXTERN void  dmgetblocksize_(DM dm,PetscInt *bs, int *ierr)
{
CHKFORTRANNULLOBJECT(dm);
CHKFORTRANNULLINTEGER(bs);
*ierr = DMGetBlockSize(
	(DM)PetscToPointer((dm) ),bs);
}
PETSC_EXTERN void  dmcreateinterpolation_(DM dmc,DM dmf,Mat *mat,Vec *vec, int *ierr)
{
CHKFORTRANNULLOBJECT(dmc);
CHKFORTRANNULLOBJECT(dmf);
PetscBool mat_null = !*(void**) mat ? PETSC_TRUE : PETSC_FALSE;
CHKFORTRANNULLOBJECT(mat);
PetscBool vec_null = !*(void**) vec ? PETSC_TRUE : PETSC_FALSE;
CHKFORTRANNULLOBJECT(vec);
*ierr = DMCreateInterpolation(
	(DM)PetscToPointer((dmc) ),
	(DM)PetscToPointer((dmf) ),mat,vec);
// if C routine nullifed the object, we must set to to -2 to indicate null set in Fortran
if (! mat_null && !*(void**) mat) * (void **) mat = (void *)-2;
// if C routine nullifed the object, we must set to to -2 to indicate null set in Fortran
if (! vec_null && !*(void**) vec) * (void **) vec = (void *)-2;
}
PETSC_EXTERN void  dmcreateinterpolationscale_(DM dac,DM daf,Mat mat,Vec *scale, int *ierr)
{
CHKFORTRANNULLOBJECT(dac);
CHKFORTRANNULLOBJECT(daf);
CHKFORTRANNULLOBJECT(mat);
PetscBool scale_null = !*(void**) scale ? PETSC_TRUE : PETSC_FALSE;
CHKFORTRANNULLOBJECT(scale);
*ierr = DMCreateInterpolationScale(
	(DM)PetscToPointer((dac) ),
	(DM)PetscToPointer((daf) ),
	(Mat)PetscToPointer((mat) ),scale);
// if C routine nullifed the object, we must set to to -2 to indicate null set in Fortran
if (! scale_null && !*(void**) scale) * (void **) scale = (void *)-2;
}
PETSC_EXTERN void  dmcreaterestriction_(DM dmc,DM dmf,Mat *mat, int *ierr)
{
CHKFORTRANNULLOBJECT(dmc);
CHKFORTRANNULLOBJECT(dmf);
PetscBool mat_null = !*(void**) mat ? PETSC_TRUE : PETSC_FALSE;
CHKFORTRANNULLOBJECT(mat);
*ierr = DMCreateRestriction(
	(DM)PetscToPointer((dmc) ),
	(DM)PetscToPointer((dmf) ),mat);
// if C routine nullifed the object, we must set to to -2 to indicate null set in Fortran
if (! mat_null && !*(void**) mat) * (void **) mat = (void *)-2;
}
PETSC_EXTERN void  dmcreateinjection_(DM dac,DM daf,Mat *mat, int *ierr)
{
CHKFORTRANNULLOBJECT(dac);
CHKFORTRANNULLOBJECT(daf);
PetscBool mat_null = !*(void**) mat ? PETSC_TRUE : PETSC_FALSE;
CHKFORTRANNULLOBJECT(mat);
*ierr = DMCreateInjection(
	(DM)PetscToPointer((dac) ),
	(DM)PetscToPointer((daf) ),mat);
// if C routine nullifed the object, we must set to to -2 to indicate null set in Fortran
if (! mat_null && !*(void**) mat) * (void **) mat = (void *)-2;
}
PETSC_EXTERN void  dmcreatemassmatrix_(DM dmc,DM dmf,Mat *mat, int *ierr)
{
CHKFORTRANNULLOBJECT(dmc);
CHKFORTRANNULLOBJECT(dmf);
PetscBool mat_null = !*(void**) mat ? PETSC_TRUE : PETSC_FALSE;
CHKFORTRANNULLOBJECT(mat);
*ierr = DMCreateMassMatrix(
	(DM)PetscToPointer((dmc) ),
	(DM)PetscToPointer((dmf) ),mat);
// if C routine nullifed the object, we must set to to -2 to indicate null set in Fortran
if (! mat_null && !*(void**) mat) * (void **) mat = (void *)-2;
}
PETSC_EXTERN void  dmcreatemassmatrixlumped_(DM dm,Vec *llm,Vec *lm, int *ierr)
{
CHKFORTRANNULLOBJECT(dm);
PetscBool llm_null = !*(void**) llm ? PETSC_TRUE : PETSC_FALSE;
CHKFORTRANNULLOBJECT(llm);
PetscBool lm_null = !*(void**) lm ? PETSC_TRUE : PETSC_FALSE;
CHKFORTRANNULLOBJECT(lm);
*ierr = DMCreateMassMatrixLumped(
	(DM)PetscToPointer((dm) ),llm,lm);
// if C routine nullifed the object, we must set to to -2 to indicate null set in Fortran
if (! llm_null && !*(void**) llm) * (void **) llm = (void *)-2;
// if C routine nullifed the object, we must set to to -2 to indicate null set in Fortran
if (! lm_null && !*(void**) lm) * (void **) lm = (void *)-2;
}
PETSC_EXTERN void  dmcreatecoloring_(DM dm,ISColoringType *ctype,ISColoring *coloring, int *ierr)
{
CHKFORTRANNULLOBJECT(dm);
PetscBool coloring_null = !*(void**) coloring ? PETSC_TRUE : PETSC_FALSE;
CHKFORTRANNULLOBJECT(coloring);
*ierr = DMCreateColoring(
	(DM)PetscToPointer((dm) ),*ctype,coloring);
// if C routine nullifed the object, we must set to to -2 to indicate null set in Fortran
if (! coloring_null && !*(void**) coloring) * (void **) coloring = (void *)-2;
}
PETSC_EXTERN void  dmcreatematrix_(DM dm,Mat *mat, int *ierr)
{
CHKFORTRANNULLOBJECT(dm);
PetscBool mat_null = !*(void**) mat ? PETSC_TRUE : PETSC_FALSE;
CHKFORTRANNULLOBJECT(mat);
*ierr = DMCreateMatrix(
	(DM)PetscToPointer((dm) ),mat);
// if C routine nullifed the object, we must set to to -2 to indicate null set in Fortran
if (! mat_null && !*(void**) mat) * (void **) mat = (void *)-2;
}
PETSC_EXTERN void  dmsetmatrixpreallocateskip_(DM dm,PetscBool *skip, int *ierr)
{
CHKFORTRANNULLOBJECT(dm);
*ierr = DMSetMatrixPreallocateSkip(
	(DM)PetscToPointer((dm) ),*skip);
}
PETSC_EXTERN void  dmsetmatrixpreallocateonly_(DM dm,PetscBool *only, int *ierr)
{
CHKFORTRANNULLOBJECT(dm);
*ierr = DMSetMatrixPreallocateOnly(
	(DM)PetscToPointer((dm) ),*only);
}
PETSC_EXTERN void  dmsetmatrixstructureonly_(DM dm,PetscBool *only, int *ierr)
{
CHKFORTRANNULLOBJECT(dm);
*ierr = DMSetMatrixStructureOnly(
	(DM)PetscToPointer((dm) ),*only);
}
PETSC_EXTERN void  dmsetblockingtype_(DM dm,DMBlockingType *btype, int *ierr)
{
CHKFORTRANNULLOBJECT(dm);
*ierr = DMSetBlockingType(
	(DM)PetscToPointer((dm) ),*btype);
}
PETSC_EXTERN void  dmgetblockingtype_(DM dm,DMBlockingType *btype, int *ierr)
{
CHKFORTRANNULLOBJECT(dm);
*ierr = DMGetBlockingType(
	(DM)PetscToPointer((dm) ),btype);
}
PETSC_EXTERN void  dmcreatesubdm_(DM dm,PetscInt *numFields, PetscInt fields[],IS *is,DM *subdm, int *ierr)
{
CHKFORTRANNULLOBJECT(dm);
CHKFORTRANNULLINTEGER(fields);
PetscBool is_null = !*(void**) is ? PETSC_TRUE : PETSC_FALSE;
CHKFORTRANNULLOBJECT(is);
PetscBool subdm_null = !*(void**) subdm ? PETSC_TRUE : PETSC_FALSE;
CHKFORTRANNULLOBJECT(subdm);
*ierr = DMCreateSubDM(
	(DM)PetscToPointer((dm) ),*numFields,fields,is,subdm);
// if C routine nullifed the object, we must set to to -2 to indicate null set in Fortran
if (! is_null && !*(void**) is) * (void **) is = (void *)-2;
// if C routine nullifed the object, we must set to to -2 to indicate null set in Fortran
if (! subdm_null && !*(void**) subdm) * (void **) subdm = (void *)-2;
}
PETSC_EXTERN void  dmrefine_(DM dm,MPI_Fint * comm,DM *dmf, int *ierr)
{
CHKFORTRANNULLOBJECT(dm);
PetscBool dmf_null = !*(void**) dmf ? PETSC_TRUE : PETSC_FALSE;
CHKFORTRANNULLOBJECT(dmf);
*ierr = DMRefine(
	(DM)PetscToPointer((dm) ),
	MPI_Comm_f2c(*(comm)),dmf);
// if C routine nullifed the object, we must set to to -2 to indicate null set in Fortran
if (! dmf_null && !*(void**) dmf) * (void **) dmf = (void *)-2;
}
PETSC_EXTERN void  dminterpolate_(DM coarse,Mat interp,DM fine, int *ierr)
{
CHKFORTRANNULLOBJECT(coarse);
CHKFORTRANNULLOBJECT(interp);
CHKFORTRANNULLOBJECT(fine);
*ierr = DMInterpolate(
	(DM)PetscToPointer((coarse) ),
	(Mat)PetscToPointer((interp) ),
	(DM)PetscToPointer((fine) ));
}
PETSC_EXTERN void  dminterpolatesolution_(DM coarse,DM fine,Mat interp,Vec coarseSol,Vec fineSol, int *ierr)
{
CHKFORTRANNULLOBJECT(coarse);
CHKFORTRANNULLOBJECT(fine);
CHKFORTRANNULLOBJECT(interp);
CHKFORTRANNULLOBJECT(coarseSol);
CHKFORTRANNULLOBJECT(fineSol);
*ierr = DMInterpolateSolution(
	(DM)PetscToPointer((coarse) ),
	(DM)PetscToPointer((fine) ),
	(Mat)PetscToPointer((interp) ),
	(Vec)PetscToPointer((coarseSol) ),
	(Vec)PetscToPointer((fineSol) ));
}
PETSC_EXTERN void  dmgetrefinelevel_(DM dm,PetscInt *level, int *ierr)
{
CHKFORTRANNULLOBJECT(dm);
CHKFORTRANNULLINTEGER(level);
*ierr = DMGetRefineLevel(
	(DM)PetscToPointer((dm) ),level);
}
PETSC_EXTERN void  dmsetrefinelevel_(DM dm,PetscInt *level, int *ierr)
{
CHKFORTRANNULLOBJECT(dm);
*ierr = DMSetRefineLevel(
	(DM)PetscToPointer((dm) ),*level);
}
PETSC_EXTERN void  dmextrude_(DM dm,PetscInt *layers,DM *dme, int *ierr)
{
CHKFORTRANNULLOBJECT(dm);
PetscBool dme_null = !*(void**) dme ? PETSC_TRUE : PETSC_FALSE;
CHKFORTRANNULLOBJECT(dme);
*ierr = DMExtrude(
	(DM)PetscToPointer((dm) ),*layers,dme);
// if C routine nullifed the object, we must set to to -2 to indicate null set in Fortran
if (! dme_null && !*(void**) dme) * (void **) dme = (void *)-2;
}
PETSC_EXTERN void  dmhasbasistransform_(DM dm,PetscBool *flg, int *ierr)
{
CHKFORTRANNULLOBJECT(dm);
*ierr = DMHasBasisTransform(
	(DM)PetscToPointer((dm) ),flg);
}
PETSC_EXTERN void  dmglobaltolocal_(DM dm,Vec g,InsertMode *mode,Vec l, int *ierr)
{
CHKFORTRANNULLOBJECT(dm);
CHKFORTRANNULLOBJECT(g);
CHKFORTRANNULLOBJECT(l);
*ierr = DMGlobalToLocal(
	(DM)PetscToPointer((dm) ),
	(Vec)PetscToPointer((g) ),*mode,
	(Vec)PetscToPointer((l) ));
}
PETSC_EXTERN void  dmglobaltolocalbegin_(DM dm,Vec g,InsertMode *mode,Vec l, int *ierr)
{
CHKFORTRANNULLOBJECT(dm);
CHKFORTRANNULLOBJECT(g);
CHKFORTRANNULLOBJECT(l);
*ierr = DMGlobalToLocalBegin(
	(DM)PetscToPointer((dm) ),
	(Vec)PetscToPointer((g) ),*mode,
	(Vec)PetscToPointer((l) ));
}
PETSC_EXTERN void  dmglobaltolocalend_(DM dm,Vec g,InsertMode *mode,Vec l, int *ierr)
{
CHKFORTRANNULLOBJECT(dm);
CHKFORTRANNULLOBJECT(g);
CHKFORTRANNULLOBJECT(l);
*ierr = DMGlobalToLocalEnd(
	(DM)PetscToPointer((dm) ),
	(Vec)PetscToPointer((g) ),*mode,
	(Vec)PetscToPointer((l) ));
}
PETSC_EXTERN void  dmlocaltoglobal_(DM dm,Vec l,InsertMode *mode,Vec g, int *ierr)
{
CHKFORTRANNULLOBJECT(dm);
CHKFORTRANNULLOBJECT(l);
CHKFORTRANNULLOBJECT(g);
*ierr = DMLocalToGlobal(
	(DM)PetscToPointer((dm) ),
	(Vec)PetscToPointer((l) ),*mode,
	(Vec)PetscToPointer((g) ));
}
PETSC_EXTERN void  dmlocaltoglobalbegin_(DM dm,Vec l,InsertMode *mode,Vec g, int *ierr)
{
CHKFORTRANNULLOBJECT(dm);
CHKFORTRANNULLOBJECT(l);
CHKFORTRANNULLOBJECT(g);
*ierr = DMLocalToGlobalBegin(
	(DM)PetscToPointer((dm) ),
	(Vec)PetscToPointer((l) ),*mode,
	(Vec)PetscToPointer((g) ));
}
PETSC_EXTERN void  dmlocaltoglobalend_(DM dm,Vec l,InsertMode *mode,Vec g, int *ierr)
{
CHKFORTRANNULLOBJECT(dm);
CHKFORTRANNULLOBJECT(l);
CHKFORTRANNULLOBJECT(g);
*ierr = DMLocalToGlobalEnd(
	(DM)PetscToPointer((dm) ),
	(Vec)PetscToPointer((l) ),*mode,
	(Vec)PetscToPointer((g) ));
}
PETSC_EXTERN void  dmlocaltolocalbegin_(DM dm,Vec g,InsertMode *mode,Vec l, int *ierr)
{
CHKFORTRANNULLOBJECT(dm);
CHKFORTRANNULLOBJECT(g);
CHKFORTRANNULLOBJECT(l);
*ierr = DMLocalToLocalBegin(
	(DM)PetscToPointer((dm) ),
	(Vec)PetscToPointer((g) ),*mode,
	(Vec)PetscToPointer((l) ));
}
PETSC_EXTERN void  dmlocaltolocalend_(DM dm,Vec g,InsertMode *mode,Vec l, int *ierr)
{
CHKFORTRANNULLOBJECT(dm);
CHKFORTRANNULLOBJECT(g);
CHKFORTRANNULLOBJECT(l);
*ierr = DMLocalToLocalEnd(
	(DM)PetscToPointer((dm) ),
	(Vec)PetscToPointer((g) ),*mode,
	(Vec)PetscToPointer((l) ));
}
PETSC_EXTERN void  dmcoarsen_(DM dm,MPI_Fint * comm,DM *dmc, int *ierr)
{
CHKFORTRANNULLOBJECT(dm);
PetscBool dmc_null = !*(void**) dmc ? PETSC_TRUE : PETSC_FALSE;
CHKFORTRANNULLOBJECT(dmc);
*ierr = DMCoarsen(
	(DM)PetscToPointer((dm) ),
	MPI_Comm_f2c(*(comm)),dmc);
// if C routine nullifed the object, we must set to to -2 to indicate null set in Fortran
if (! dmc_null && !*(void**) dmc) * (void **) dmc = (void *)-2;
}
PETSC_EXTERN void  dmrestrict_(DM fine,Mat restrct,Vec rscale,Mat inject,DM coarse, int *ierr)
{
CHKFORTRANNULLOBJECT(fine);
CHKFORTRANNULLOBJECT(restrct);
CHKFORTRANNULLOBJECT(rscale);
CHKFORTRANNULLOBJECT(inject);
CHKFORTRANNULLOBJECT(coarse);
*ierr = DMRestrict(
	(DM)PetscToPointer((fine) ),
	(Mat)PetscToPointer((restrct) ),
	(Vec)PetscToPointer((rscale) ),
	(Mat)PetscToPointer((inject) ),
	(DM)PetscToPointer((coarse) ));
}
PETSC_EXTERN void  dmsubdomainrestrict_(DM global,VecScatter *oscatter,VecScatter *gscatter,DM subdm, int *ierr)
{
CHKFORTRANNULLOBJECT(global);
CHKFORTRANNULLOBJECT(subdm);
*ierr = DMSubDomainRestrict(
	(DM)PetscToPointer((global) ),*oscatter,*gscatter,
	(DM)PetscToPointer((subdm) ));
}
PETSC_EXTERN void  dmgetcoarsenlevel_(DM dm,PetscInt *level, int *ierr)
{
CHKFORTRANNULLOBJECT(dm);
CHKFORTRANNULLINTEGER(level);
*ierr = DMGetCoarsenLevel(
	(DM)PetscToPointer((dm) ),level);
}
PETSC_EXTERN void  dmsetcoarsenlevel_(DM dm,PetscInt *level, int *ierr)
{
CHKFORTRANNULLOBJECT(dm);
*ierr = DMSetCoarsenLevel(
	(DM)PetscToPointer((dm) ),*level);
}
PETSC_EXTERN void  dmrefinehierarchy_(DM dm,PetscInt *nlevels,DM dmf[], int *ierr)
{
CHKFORTRANNULLOBJECT(dm);
PetscBool dmf_null = !*(void**) dmf ? PETSC_TRUE : PETSC_FALSE;
CHKFORTRANNULLOBJECT(dmf);
*ierr = DMRefineHierarchy(
	(DM)PetscToPointer((dm) ),*nlevels,dmf);
// if C routine nullifed the object, we must set to to -2 to indicate null set in Fortran
if (! dmf_null && !*(void**) dmf) * (void **) dmf = (void *)-2;
}
PETSC_EXTERN void  dmcoarsenhierarchy_(DM dm,PetscInt *nlevels,DM dmc[], int *ierr)
{
CHKFORTRANNULLOBJECT(dm);
PetscBool dmc_null = !*(void**) dmc ? PETSC_TRUE : PETSC_FALSE;
CHKFORTRANNULLOBJECT(dmc);
*ierr = DMCoarsenHierarchy(
	(DM)PetscToPointer((dm) ),*nlevels,dmc);
// if C routine nullifed the object, we must set to to -2 to indicate null set in Fortran
if (! dmc_null && !*(void**) dmc) * (void **) dmc = (void *)-2;
}
PETSC_EXTERN void  dmsetapplicationcontext_(DM dm,void*ctx, int *ierr)
{
CHKFORTRANNULLOBJECT(dm);
*ierr = DMSetApplicationContext(
	(DM)PetscToPointer((dm) ),ctx);
}
PETSC_EXTERN void  dmgetapplicationcontext_(DM dm,void*ctx, int *ierr)
{
CHKFORTRANNULLOBJECT(dm);
*ierr = DMGetApplicationContext(
	(DM)PetscToPointer((dm) ),ctx);
}
PETSC_EXTERN void  dmhasvariablebounds_(DM dm,PetscBool *flg, int *ierr)
{
CHKFORTRANNULLOBJECT(dm);
*ierr = DMHasVariableBounds(
	(DM)PetscToPointer((dm) ),flg);
}
PETSC_EXTERN void  dmcomputevariablebounds_(DM dm,Vec xl,Vec xu, int *ierr)
{
CHKFORTRANNULLOBJECT(dm);
CHKFORTRANNULLOBJECT(xl);
CHKFORTRANNULLOBJECT(xu);
*ierr = DMComputeVariableBounds(
	(DM)PetscToPointer((dm) ),
	(Vec)PetscToPointer((xl) ),
	(Vec)PetscToPointer((xu) ));
}
PETSC_EXTERN void  dmhascoloring_(DM dm,PetscBool *flg, int *ierr)
{
CHKFORTRANNULLOBJECT(dm);
*ierr = DMHasColoring(
	(DM)PetscToPointer((dm) ),flg);
}
PETSC_EXTERN void  dmhascreaterestriction_(DM dm,PetscBool *flg, int *ierr)
{
CHKFORTRANNULLOBJECT(dm);
*ierr = DMHasCreateRestriction(
	(DM)PetscToPointer((dm) ),flg);
}
PETSC_EXTERN void  dmhascreateinjection_(DM dm,PetscBool *flg, int *ierr)
{
CHKFORTRANNULLOBJECT(dm);
*ierr = DMHasCreateInjection(
	(DM)PetscToPointer((dm) ),flg);
}
PETSC_EXTERN void  dmsettype_(DM dm,char *method, int *ierr, PETSC_FORTRAN_CHARLEN_T cl0)
{
  char *_cltmp0 = PETSC_NULLPTR;
CHKFORTRANNULLOBJECT(dm);
/* insert Fortran-to-C conversion for method */
  FIXCHAR(method,cl0,_cltmp0);
*ierr = DMSetType(
	(DM)PetscToPointer((dm) ),_cltmp0);
  FREECHAR(method,_cltmp0);
}
PETSC_EXTERN void  dmgettype_(DM dm,char *type, int *ierr, PETSC_FORTRAN_CHARLEN_T cl0)
{
  char *_cltmp0 = PETSC_NULLPTR;
CHKFORTRANNULLOBJECT(dm);
*ierr = DMGetType(
	(DM)PetscToPointer((dm) ),(const char **)&_cltmp0);
/* insert C-to-Fortran conversion for type */
*ierr = PetscStrncpy(type, _cltmp0, cl0);
                        if (*ierr) return;
                        FIXRETURNCHAR(PETSC_TRUE, type, cl0);
}
PETSC_EXTERN void  dmconvert_(DM dm,char *newtype,DM *M, int *ierr, PETSC_FORTRAN_CHARLEN_T cl0)
{
  char *_cltmp0 = PETSC_NULLPTR;
CHKFORTRANNULLOBJECT(dm);
PetscBool M_null = !*(void**) M ? PETSC_TRUE : PETSC_FALSE;
CHKFORTRANNULLOBJECT(M);
/* insert Fortran-to-C conversion for newtype */
  FIXCHAR(newtype,cl0,_cltmp0);
*ierr = DMConvert(
	(DM)PetscToPointer((dm) ),_cltmp0,M);
  FREECHAR(newtype,_cltmp0);
// if C routine nullifed the object, we must set to to -2 to indicate null set in Fortran
if (! M_null && !*(void**) M) * (void **) M = (void *)-2;
}
PETSC_EXTERN void  dmload_(DM newdm,PetscViewer viewer, int *ierr)
{
CHKFORTRANNULLOBJECT(newdm);
CHKFORTRANNULLOBJECT(viewer);
*ierr = DMLoad(
	(DM)PetscToPointer((newdm) ),PetscPatchDefaultViewers((PetscViewer*)viewer));
}
PETSC_EXTERN void  dmgetsection_(DM dm,PetscSection *section, int *ierr)
{
CHKFORTRANNULLOBJECT(dm);
PetscBool section_null = !*(void**) section ? PETSC_TRUE : PETSC_FALSE;
CHKFORTRANNULLOBJECT(section);
*ierr = DMGetSection(
	(DM)PetscToPointer((dm) ),section);
// if C routine nullifed the object, we must set to to -2 to indicate null set in Fortran
if (! section_null && !*(void**) section) * (void **) section = (void *)-2;
}
PETSC_EXTERN void  dmgetlocalsection_(DM dm,PetscSection *section, int *ierr)
{
CHKFORTRANNULLOBJECT(dm);
PetscBool section_null = !*(void**) section ? PETSC_TRUE : PETSC_FALSE;
CHKFORTRANNULLOBJECT(section);
*ierr = DMGetLocalSection(
	(DM)PetscToPointer((dm) ),section);
// if C routine nullifed the object, we must set to to -2 to indicate null set in Fortran
if (! section_null && !*(void**) section) * (void **) section = (void *)-2;
}
PETSC_EXTERN void  dmsetsection_(DM dm,PetscSection section, int *ierr)
{
CHKFORTRANNULLOBJECT(dm);
CHKFORTRANNULLOBJECT(section);
*ierr = DMSetSection(
	(DM)PetscToPointer((dm) ),
	(PetscSection)PetscToPointer((section) ));
}
PETSC_EXTERN void  dmsetlocalsection_(DM dm,PetscSection section, int *ierr)
{
CHKFORTRANNULLOBJECT(dm);
CHKFORTRANNULLOBJECT(section);
*ierr = DMSetLocalSection(
	(DM)PetscToPointer((dm) ),
	(PetscSection)PetscToPointer((section) ));
}
PETSC_EXTERN void  dmgetdefaultconstraints_(DM dm,PetscSection *section,Mat *mat,Vec *bias, int *ierr)
{
CHKFORTRANNULLOBJECT(dm);
PetscBool section_null = !*(void**) section ? PETSC_TRUE : PETSC_FALSE;
CHKFORTRANNULLOBJECT(section);
PetscBool mat_null = !*(void**) mat ? PETSC_TRUE : PETSC_FALSE;
CHKFORTRANNULLOBJECT(mat);
PetscBool bias_null = !*(void**) bias ? PETSC_TRUE : PETSC_FALSE;
CHKFORTRANNULLOBJECT(bias);
*ierr = DMGetDefaultConstraints(
	(DM)PetscToPointer((dm) ),section,mat,bias);
// if C routine nullifed the object, we must set to to -2 to indicate null set in Fortran
if (! section_null && !*(void**) section) * (void **) section = (void *)-2;
// if C routine nullifed the object, we must set to to -2 to indicate null set in Fortran
if (! mat_null && !*(void**) mat) * (void **) mat = (void *)-2;
// if C routine nullifed the object, we must set to to -2 to indicate null set in Fortran
if (! bias_null && !*(void**) bias) * (void **) bias = (void *)-2;
}
PETSC_EXTERN void  dmsetdefaultconstraints_(DM dm,PetscSection section,Mat mat,Vec bias, int *ierr)
{
CHKFORTRANNULLOBJECT(dm);
CHKFORTRANNULLOBJECT(section);
CHKFORTRANNULLOBJECT(mat);
CHKFORTRANNULLOBJECT(bias);
*ierr = DMSetDefaultConstraints(
	(DM)PetscToPointer((dm) ),
	(PetscSection)PetscToPointer((section) ),
	(Mat)PetscToPointer((mat) ),
	(Vec)PetscToPointer((bias) ));
}
PETSC_EXTERN void  dmgetglobalsection_(DM dm,PetscSection *section, int *ierr)
{
CHKFORTRANNULLOBJECT(dm);
PetscBool section_null = !*(void**) section ? PETSC_TRUE : PETSC_FALSE;
CHKFORTRANNULLOBJECT(section);
*ierr = DMGetGlobalSection(
	(DM)PetscToPointer((dm) ),section);
// if C routine nullifed the object, we must set to to -2 to indicate null set in Fortran
if (! section_null && !*(void**) section) * (void **) section = (void *)-2;
}
PETSC_EXTERN void  dmsetglobalsection_(DM dm,PetscSection section, int *ierr)
{
CHKFORTRANNULLOBJECT(dm);
CHKFORTRANNULLOBJECT(section);
*ierr = DMSetGlobalSection(
	(DM)PetscToPointer((dm) ),
	(PetscSection)PetscToPointer((section) ));
}
PETSC_EXTERN void  dmgetsectionsf_(DM dm,PetscSF *sf, int *ierr)
{
CHKFORTRANNULLOBJECT(dm);
PetscBool sf_null = !*(void**) sf ? PETSC_TRUE : PETSC_FALSE;
CHKFORTRANNULLOBJECT(sf);
*ierr = DMGetSectionSF(
	(DM)PetscToPointer((dm) ),sf);
// if C routine nullifed the object, we must set to to -2 to indicate null set in Fortran
if (! sf_null && !*(void**) sf) * (void **) sf = (void *)-2;
}
PETSC_EXTERN void  dmsetsectionsf_(DM dm,PetscSF sf, int *ierr)
{
CHKFORTRANNULLOBJECT(dm);
CHKFORTRANNULLOBJECT(sf);
*ierr = DMSetSectionSF(
	(DM)PetscToPointer((dm) ),
	(PetscSF)PetscToPointer((sf) ));
}
PETSC_EXTERN void  dmcreatesectionsf_(DM dm,PetscSection localSection,PetscSection globalSection, int *ierr)
{
CHKFORTRANNULLOBJECT(dm);
CHKFORTRANNULLOBJECT(localSection);
CHKFORTRANNULLOBJECT(globalSection);
*ierr = DMCreateSectionSF(
	(DM)PetscToPointer((dm) ),
	(PetscSection)PetscToPointer((localSection) ),
	(PetscSection)PetscToPointer((globalSection) ));
}
PETSC_EXTERN void  dmgetpointsf_(DM dm,PetscSF *sf, int *ierr)
{
CHKFORTRANNULLOBJECT(dm);
PetscBool sf_null = !*(void**) sf ? PETSC_TRUE : PETSC_FALSE;
CHKFORTRANNULLOBJECT(sf);
*ierr = DMGetPointSF(
	(DM)PetscToPointer((dm) ),sf);
// if C routine nullifed the object, we must set to to -2 to indicate null set in Fortran
if (! sf_null && !*(void**) sf) * (void **) sf = (void *)-2;
}
PETSC_EXTERN void  dmsetpointsf_(DM dm,PetscSF sf, int *ierr)
{
CHKFORTRANNULLOBJECT(dm);
CHKFORTRANNULLOBJECT(sf);
*ierr = DMSetPointSF(
	(DM)PetscToPointer((dm) ),
	(PetscSF)PetscToPointer((sf) ));
}
PETSC_EXTERN void  dmgetnaturalsf_(DM dm,PetscSF *sf, int *ierr)
{
CHKFORTRANNULLOBJECT(dm);
PetscBool sf_null = !*(void**) sf ? PETSC_TRUE : PETSC_FALSE;
CHKFORTRANNULLOBJECT(sf);
*ierr = DMGetNaturalSF(
	(DM)PetscToPointer((dm) ),sf);
// if C routine nullifed the object, we must set to to -2 to indicate null set in Fortran
if (! sf_null && !*(void**) sf) * (void **) sf = (void *)-2;
}
PETSC_EXTERN void  dmsetnaturalsf_(DM dm,PetscSF sf, int *ierr)
{
CHKFORTRANNULLOBJECT(dm);
CHKFORTRANNULLOBJECT(sf);
*ierr = DMSetNaturalSF(
	(DM)PetscToPointer((dm) ),
	(PetscSF)PetscToPointer((sf) ));
}
PETSC_EXTERN void  dmclearfields_(DM dm, int *ierr)
{
CHKFORTRANNULLOBJECT(dm);
*ierr = DMClearFields(
	(DM)PetscToPointer((dm) ));
}
PETSC_EXTERN void  dmgetnumfields_(DM dm,PetscInt *numFields, int *ierr)
{
CHKFORTRANNULLOBJECT(dm);
CHKFORTRANNULLINTEGER(numFields);
*ierr = DMGetNumFields(
	(DM)PetscToPointer((dm) ),numFields);
}
PETSC_EXTERN void  dmsetnumfields_(DM dm,PetscInt *numFields, int *ierr)
{
CHKFORTRANNULLOBJECT(dm);
*ierr = DMSetNumFields(
	(DM)PetscToPointer((dm) ),*numFields);
}
PETSC_EXTERN void  dmgetfield_(DM dm,PetscInt *f,DMLabel *label,PetscObject *disc, int *ierr)
{
CHKFORTRANNULLOBJECT(dm);
PetscBool label_null = !*(void**) label ? PETSC_TRUE : PETSC_FALSE;
CHKFORTRANNULLOBJECT(label);
PetscBool disc_null = !*(void**) disc ? PETSC_TRUE : PETSC_FALSE;
CHKFORTRANNULLOBJECT(disc);
*ierr = DMGetField(
	(DM)PetscToPointer((dm) ),*f,label,disc);
// if C routine nullifed the object, we must set to to -2 to indicate null set in Fortran
if (! label_null && !*(void**) label) * (void **) label = (void *)-2;
// if C routine nullifed the object, we must set to to -2 to indicate null set in Fortran
if (! disc_null && !*(void**) disc) * (void **) disc = (void *)-2;
}
PETSC_EXTERN void  dmsetfield_(DM dm,PetscInt *f,DMLabel label,PetscObject disc, int *ierr)
{
CHKFORTRANNULLOBJECT(dm);
CHKFORTRANNULLOBJECT(label);
CHKFORTRANNULLOBJECT(disc);
*ierr = DMSetField(
	(DM)PetscToPointer((dm) ),*f,
	(DMLabel)PetscToPointer((label) ),
	(PetscObject)PetscToPointer((disc) ));
}
PETSC_EXTERN void  dmaddfield_(DM dm,DMLabel label,PetscObject disc, int *ierr)
{
CHKFORTRANNULLOBJECT(dm);
CHKFORTRANNULLOBJECT(label);
CHKFORTRANNULLOBJECT(disc);
*ierr = DMAddField(
	(DM)PetscToPointer((dm) ),
	(DMLabel)PetscToPointer((label) ),
	(PetscObject)PetscToPointer((disc) ));
}
PETSC_EXTERN void  dmsetfieldavoidtensor_(DM dm,PetscInt *f,PetscBool *avoidTensor, int *ierr)
{
CHKFORTRANNULLOBJECT(dm);
*ierr = DMSetFieldAvoidTensor(
	(DM)PetscToPointer((dm) ),*f,*avoidTensor);
}
PETSC_EXTERN void  dmgetfieldavoidtensor_(DM dm,PetscInt *f,PetscBool *avoidTensor, int *ierr)
{
CHKFORTRANNULLOBJECT(dm);
*ierr = DMGetFieldAvoidTensor(
	(DM)PetscToPointer((dm) ),*f,avoidTensor);
}
PETSC_EXTERN void  dmcopyfields_(DM dm,PetscInt *minDegree,PetscInt *maxDegree,DM newdm, int *ierr)
{
CHKFORTRANNULLOBJECT(dm);
CHKFORTRANNULLOBJECT(newdm);
*ierr = DMCopyFields(
	(DM)PetscToPointer((dm) ),*minDegree,*maxDegree,
	(DM)PetscToPointer((newdm) ));
}
PETSC_EXTERN void  dmgetadjacency_(DM dm,PetscInt *f,PetscBool *useCone,PetscBool *useClosure, int *ierr)
{
CHKFORTRANNULLOBJECT(dm);
*ierr = DMGetAdjacency(
	(DM)PetscToPointer((dm) ),*f,useCone,useClosure);
}
PETSC_EXTERN void  dmsetadjacency_(DM dm,PetscInt *f,PetscBool *useCone,PetscBool *useClosure, int *ierr)
{
CHKFORTRANNULLOBJECT(dm);
*ierr = DMSetAdjacency(
	(DM)PetscToPointer((dm) ),*f,*useCone,*useClosure);
}
PETSC_EXTERN void  dmgetbasicadjacency_(DM dm,PetscBool *useCone,PetscBool *useClosure, int *ierr)
{
CHKFORTRANNULLOBJECT(dm);
*ierr = DMGetBasicAdjacency(
	(DM)PetscToPointer((dm) ),useCone,useClosure);
}
PETSC_EXTERN void  dmsetbasicadjacency_(DM dm,PetscBool *useCone,PetscBool *useClosure, int *ierr)
{
CHKFORTRANNULLOBJECT(dm);
*ierr = DMSetBasicAdjacency(
	(DM)PetscToPointer((dm) ),*useCone,*useClosure);
}
PETSC_EXTERN void  dmgetnumds_(DM dm,PetscInt *Nds, int *ierr)
{
CHKFORTRANNULLOBJECT(dm);
CHKFORTRANNULLINTEGER(Nds);
*ierr = DMGetNumDS(
	(DM)PetscToPointer((dm) ),Nds);
}
PETSC_EXTERN void  dmcleards_(DM dm, int *ierr)
{
CHKFORTRANNULLOBJECT(dm);
*ierr = DMClearDS(
	(DM)PetscToPointer((dm) ));
}
PETSC_EXTERN void  dmgetds_(DM dm,PetscDS *ds, int *ierr)
{
CHKFORTRANNULLOBJECT(dm);
PetscBool ds_null = !*(void**) ds ? PETSC_TRUE : PETSC_FALSE;
CHKFORTRANNULLOBJECT(ds);
*ierr = DMGetDS(
	(DM)PetscToPointer((dm) ),ds);
// if C routine nullifed the object, we must set to to -2 to indicate null set in Fortran
if (! ds_null && !*(void**) ds) * (void **) ds = (void *)-2;
}
PETSC_EXTERN void  dmgetcellds_(DM dm,PetscInt *point,PetscDS *ds,PetscDS *dsIn, int *ierr)
{
CHKFORTRANNULLOBJECT(dm);
PetscBool ds_null = !*(void**) ds ? PETSC_TRUE : PETSC_FALSE;
CHKFORTRANNULLOBJECT(ds);
PetscBool dsIn_null = !*(void**) dsIn ? PETSC_TRUE : PETSC_FALSE;
CHKFORTRANNULLOBJECT(dsIn);
*ierr = DMGetCellDS(
	(DM)PetscToPointer((dm) ),*point,ds,dsIn);
// if C routine nullifed the object, we must set to to -2 to indicate null set in Fortran
if (! ds_null && !*(void**) ds) * (void **) ds = (void *)-2;
// if C routine nullifed the object, we must set to to -2 to indicate null set in Fortran
if (! dsIn_null && !*(void**) dsIn) * (void **) dsIn = (void *)-2;
}
PETSC_EXTERN void  dmgetregionds_(DM dm,DMLabel label,IS *fields,PetscDS *ds,PetscDS *dsIn, int *ierr)
{
CHKFORTRANNULLOBJECT(dm);
CHKFORTRANNULLOBJECT(label);
PetscBool fields_null = !*(void**) fields ? PETSC_TRUE : PETSC_FALSE;
CHKFORTRANNULLOBJECT(fields);
PetscBool ds_null = !*(void**) ds ? PETSC_TRUE : PETSC_FALSE;
CHKFORTRANNULLOBJECT(ds);
PetscBool dsIn_null = !*(void**) dsIn ? PETSC_TRUE : PETSC_FALSE;
CHKFORTRANNULLOBJECT(dsIn);
*ierr = DMGetRegionDS(
	(DM)PetscToPointer((dm) ),
	(DMLabel)PetscToPointer((label) ),fields,ds,dsIn);
// if C routine nullifed the object, we must set to to -2 to indicate null set in Fortran
if (! fields_null && !*(void**) fields) * (void **) fields = (void *)-2;
// if C routine nullifed the object, we must set to to -2 to indicate null set in Fortran
if (! ds_null && !*(void**) ds) * (void **) ds = (void *)-2;
// if C routine nullifed the object, we must set to to -2 to indicate null set in Fortran
if (! dsIn_null && !*(void**) dsIn) * (void **) dsIn = (void *)-2;
}
PETSC_EXTERN void  dmsetregionds_(DM dm,DMLabel label,IS fields,PetscDS ds,PetscDS dsIn, int *ierr)
{
CHKFORTRANNULLOBJECT(dm);
CHKFORTRANNULLOBJECT(label);
CHKFORTRANNULLOBJECT(fields);
CHKFORTRANNULLOBJECT(ds);
CHKFORTRANNULLOBJECT(dsIn);
*ierr = DMSetRegionDS(
	(DM)PetscToPointer((dm) ),
	(DMLabel)PetscToPointer((label) ),
	(IS)PetscToPointer((fields) ),
	(PetscDS)PetscToPointer((ds) ),
	(PetscDS)PetscToPointer((dsIn) ));
}
PETSC_EXTERN void  dmgetregionnumds_(DM dm,PetscInt *num,DMLabel *label,IS *fields,PetscDS *ds,PetscDS *dsIn, int *ierr)
{
CHKFORTRANNULLOBJECT(dm);
PetscBool label_null = !*(void**) label ? PETSC_TRUE : PETSC_FALSE;
CHKFORTRANNULLOBJECT(label);
PetscBool fields_null = !*(void**) fields ? PETSC_TRUE : PETSC_FALSE;
CHKFORTRANNULLOBJECT(fields);
PetscBool ds_null = !*(void**) ds ? PETSC_TRUE : PETSC_FALSE;
CHKFORTRANNULLOBJECT(ds);
PetscBool dsIn_null = !*(void**) dsIn ? PETSC_TRUE : PETSC_FALSE;
CHKFORTRANNULLOBJECT(dsIn);
*ierr = DMGetRegionNumDS(
	(DM)PetscToPointer((dm) ),*num,label,fields,ds,dsIn);
// if C routine nullifed the object, we must set to to -2 to indicate null set in Fortran
if (! label_null && !*(void**) label) * (void **) label = (void *)-2;
// if C routine nullifed the object, we must set to to -2 to indicate null set in Fortran
if (! fields_null && !*(void**) fields) * (void **) fields = (void *)-2;
// if C routine nullifed the object, we must set to to -2 to indicate null set in Fortran
if (! ds_null && !*(void**) ds) * (void **) ds = (void *)-2;
// if C routine nullifed the object, we must set to to -2 to indicate null set in Fortran
if (! dsIn_null && !*(void**) dsIn) * (void **) dsIn = (void *)-2;
}
PETSC_EXTERN void  dmsetregionnumds_(DM dm,PetscInt *num,DMLabel label,IS fields,PetscDS ds,PetscDS dsIn, int *ierr)
{
CHKFORTRANNULLOBJECT(dm);
CHKFORTRANNULLOBJECT(label);
CHKFORTRANNULLOBJECT(fields);
CHKFORTRANNULLOBJECT(ds);
CHKFORTRANNULLOBJECT(dsIn);
*ierr = DMSetRegionNumDS(
	(DM)PetscToPointer((dm) ),*num,
	(DMLabel)PetscToPointer((label) ),
	(IS)PetscToPointer((fields) ),
	(PetscDS)PetscToPointer((ds) ),
	(PetscDS)PetscToPointer((dsIn) ));
}
PETSC_EXTERN void  dmfindregionnum_(DM dm,PetscDS ds,PetscInt *num, int *ierr)
{
CHKFORTRANNULLOBJECT(dm);
CHKFORTRANNULLOBJECT(ds);
CHKFORTRANNULLINTEGER(num);
*ierr = DMFindRegionNum(
	(DM)PetscToPointer((dm) ),
	(PetscDS)PetscToPointer((ds) ),num);
}
PETSC_EXTERN void  dmcreatefedefault_(DM dm,PetscInt *Nc, char prefix[],PetscInt *qorder,PetscFE *fem, int *ierr, PETSC_FORTRAN_CHARLEN_T cl0)
{
  char *_cltmp0 = PETSC_NULLPTR;
CHKFORTRANNULLOBJECT(dm);
PetscBool fem_null = !*(void**) fem ? PETSC_TRUE : PETSC_FALSE;
CHKFORTRANNULLOBJECT(fem);
/* insert Fortran-to-C conversion for prefix */
  FIXCHAR(prefix,cl0,_cltmp0);
*ierr = DMCreateFEDefault(
	(DM)PetscToPointer((dm) ),*Nc,_cltmp0,*qorder,fem);
  FREECHAR(prefix,_cltmp0);
// if C routine nullifed the object, we must set to to -2 to indicate null set in Fortran
if (! fem_null && !*(void**) fem) * (void **) fem = (void *)-2;
}
PETSC_EXTERN void  dmcreateds_(DM dm, int *ierr)
{
CHKFORTRANNULLOBJECT(dm);
*ierr = DMCreateDS(
	(DM)PetscToPointer((dm) ));
}
PETSC_EXTERN void  dmusetensororder_(DM dm,PetscBool *tensor, int *ierr)
{
CHKFORTRANNULLOBJECT(dm);
*ierr = DMUseTensorOrder(
	(DM)PetscToPointer((dm) ),*tensor);
}
PETSC_EXTERN void  dmcomputeexactsolution_(DM dm,PetscReal *time,Vec u,Vec u_t, int *ierr)
{
CHKFORTRANNULLOBJECT(dm);
CHKFORTRANNULLOBJECT(u);
CHKFORTRANNULLOBJECT(u_t);
*ierr = DMComputeExactSolution(
	(DM)PetscToPointer((dm) ),*time,
	(Vec)PetscToPointer((u) ),
	(Vec)PetscToPointer((u_t) ));
}
PETSC_EXTERN void  dmcopyds_(DM dm,PetscInt *minDegree,PetscInt *maxDegree,DM newdm, int *ierr)
{
CHKFORTRANNULLOBJECT(dm);
CHKFORTRANNULLOBJECT(newdm);
*ierr = DMCopyDS(
	(DM)PetscToPointer((dm) ),*minDegree,*maxDegree,
	(DM)PetscToPointer((newdm) ));
}
PETSC_EXTERN void  dmcopydisc_(DM dm,DM newdm, int *ierr)
{
CHKFORTRANNULLOBJECT(dm);
CHKFORTRANNULLOBJECT(newdm);
*ierr = DMCopyDisc(
	(DM)PetscToPointer((dm) ),
	(DM)PetscToPointer((newdm) ));
}
PETSC_EXTERN void  dmgetdimension_(DM dm,PetscInt *dim, int *ierr)
{
CHKFORTRANNULLOBJECT(dm);
CHKFORTRANNULLINTEGER(dim);
*ierr = DMGetDimension(
	(DM)PetscToPointer((dm) ),dim);
}
PETSC_EXTERN void  dmsetdimension_(DM dm,PetscInt *dim, int *ierr)
{
CHKFORTRANNULLOBJECT(dm);
*ierr = DMSetDimension(
	(DM)PetscToPointer((dm) ),*dim);
}
PETSC_EXTERN void  dmgetdimpoints_(DM dm,PetscInt *dim,PetscInt *pStart,PetscInt *pEnd, int *ierr)
{
CHKFORTRANNULLOBJECT(dm);
CHKFORTRANNULLINTEGER(pStart);
CHKFORTRANNULLINTEGER(pEnd);
*ierr = DMGetDimPoints(
	(DM)PetscToPointer((dm) ),*dim,pStart,pEnd);
}
PETSC_EXTERN void  dmgetoutputdm_(DM dm,DM *odm, int *ierr)
{
CHKFORTRANNULLOBJECT(dm);
PetscBool odm_null = !*(void**) odm ? PETSC_TRUE : PETSC_FALSE;
CHKFORTRANNULLOBJECT(odm);
*ierr = DMGetOutputDM(
	(DM)PetscToPointer((dm) ),odm);
// if C routine nullifed the object, we must set to to -2 to indicate null set in Fortran
if (! odm_null && !*(void**) odm) * (void **) odm = (void *)-2;
}
PETSC_EXTERN void  dmgetoutputsequencenumber_(DM dm,PetscInt *num,PetscReal *val, int *ierr)
{
CHKFORTRANNULLOBJECT(dm);
CHKFORTRANNULLINTEGER(num);
CHKFORTRANNULLREAL(val);
*ierr = DMGetOutputSequenceNumber(
	(DM)PetscToPointer((dm) ),num,val);
}
PETSC_EXTERN void  dmsetoutputsequencenumber_(DM dm,PetscInt *num,PetscReal *val, int *ierr)
{
CHKFORTRANNULLOBJECT(dm);
*ierr = DMSetOutputSequenceNumber(
	(DM)PetscToPointer((dm) ),*num,*val);
}
PETSC_EXTERN void  dmoutputsequenceload_(DM dm,PetscViewer viewer, char name[],PetscInt *num,PetscReal *val, int *ierr, PETSC_FORTRAN_CHARLEN_T cl0)
{
  char *_cltmp0 = PETSC_NULLPTR;
CHKFORTRANNULLOBJECT(dm);
CHKFORTRANNULLOBJECT(viewer);
CHKFORTRANNULLREAL(val);
/* insert Fortran-to-C conversion for name */
  FIXCHAR(name,cl0,_cltmp0);
*ierr = DMOutputSequenceLoad(
	(DM)PetscToPointer((dm) ),PetscPatchDefaultViewers((PetscViewer*)viewer),_cltmp0,*num,val);
  FREECHAR(name,_cltmp0);
}
PETSC_EXTERN void  dmgetoutputsequencelength_(DM dm,PetscViewer viewer, char name[],PetscInt *len, int *ierr, PETSC_FORTRAN_CHARLEN_T cl0)
{
  char *_cltmp0 = PETSC_NULLPTR;
CHKFORTRANNULLOBJECT(dm);
CHKFORTRANNULLOBJECT(viewer);
CHKFORTRANNULLINTEGER(len);
/* insert Fortran-to-C conversion for name */
  FIXCHAR(name,cl0,_cltmp0);
*ierr = DMGetOutputSequenceLength(
	(DM)PetscToPointer((dm) ),PetscPatchDefaultViewers((PetscViewer*)viewer),_cltmp0,len);
  FREECHAR(name,_cltmp0);
}
PETSC_EXTERN void  dmgetusenatural_(DM dm,PetscBool *useNatural, int *ierr)
{
CHKFORTRANNULLOBJECT(dm);
*ierr = DMGetUseNatural(
	(DM)PetscToPointer((dm) ),useNatural);
}
PETSC_EXTERN void  dmsetusenatural_(DM dm,PetscBool *useNatural, int *ierr)
{
CHKFORTRANNULLOBJECT(dm);
*ierr = DMSetUseNatural(
	(DM)PetscToPointer((dm) ),*useNatural);
}
PETSC_EXTERN void  dmcreatelabel_(DM dm, char name[], int *ierr, PETSC_FORTRAN_CHARLEN_T cl0)
{
  char *_cltmp0 = PETSC_NULLPTR;
CHKFORTRANNULLOBJECT(dm);
/* insert Fortran-to-C conversion for name */
  FIXCHAR(name,cl0,_cltmp0);
*ierr = DMCreateLabel(
	(DM)PetscToPointer((dm) ),_cltmp0);
  FREECHAR(name,_cltmp0);
}
PETSC_EXTERN void  dmcreatelabelatindex_(DM dm,PetscInt *l, char name[], int *ierr, PETSC_FORTRAN_CHARLEN_T cl0)
{
  char *_cltmp0 = PETSC_NULLPTR;
CHKFORTRANNULLOBJECT(dm);
/* insert Fortran-to-C conversion for name */
  FIXCHAR(name,cl0,_cltmp0);
*ierr = DMCreateLabelAtIndex(
	(DM)PetscToPointer((dm) ),*l,_cltmp0);
  FREECHAR(name,_cltmp0);
}
PETSC_EXTERN void  dmgetlabelvalue_(DM dm, char name[],PetscInt *point,PetscInt *value, int *ierr, PETSC_FORTRAN_CHARLEN_T cl0)
{
  char *_cltmp0 = PETSC_NULLPTR;
CHKFORTRANNULLOBJECT(dm);
CHKFORTRANNULLINTEGER(value);
/* insert Fortran-to-C conversion for name */
  FIXCHAR(name,cl0,_cltmp0);
*ierr = DMGetLabelValue(
	(DM)PetscToPointer((dm) ),_cltmp0,*point,value);
  FREECHAR(name,_cltmp0);
}
PETSC_EXTERN void  dmsetlabelvalue_(DM dm, char name[],PetscInt *point,PetscInt *value, int *ierr, PETSC_FORTRAN_CHARLEN_T cl0)
{
  char *_cltmp0 = PETSC_NULLPTR;
CHKFORTRANNULLOBJECT(dm);
/* insert Fortran-to-C conversion for name */
  FIXCHAR(name,cl0,_cltmp0);
*ierr = DMSetLabelValue(
	(DM)PetscToPointer((dm) ),_cltmp0,*point,*value);
  FREECHAR(name,_cltmp0);
}
PETSC_EXTERN void  dmclearlabelvalue_(DM dm, char name[],PetscInt *point,PetscInt *value, int *ierr, PETSC_FORTRAN_CHARLEN_T cl0)
{
  char *_cltmp0 = PETSC_NULLPTR;
CHKFORTRANNULLOBJECT(dm);
/* insert Fortran-to-C conversion for name */
  FIXCHAR(name,cl0,_cltmp0);
*ierr = DMClearLabelValue(
	(DM)PetscToPointer((dm) ),_cltmp0,*point,*value);
  FREECHAR(name,_cltmp0);
}
PETSC_EXTERN void  dmgetlabelsize_(DM dm, char name[],PetscInt *size, int *ierr, PETSC_FORTRAN_CHARLEN_T cl0)
{
  char *_cltmp0 = PETSC_NULLPTR;
CHKFORTRANNULLOBJECT(dm);
CHKFORTRANNULLINTEGER(size);
/* insert Fortran-to-C conversion for name */
  FIXCHAR(name,cl0,_cltmp0);
*ierr = DMGetLabelSize(
	(DM)PetscToPointer((dm) ),_cltmp0,size);
  FREECHAR(name,_cltmp0);
}
PETSC_EXTERN void  dmgetlabelidis_(DM dm, char name[],IS *ids, int *ierr, PETSC_FORTRAN_CHARLEN_T cl0)
{
  char *_cltmp0 = PETSC_NULLPTR;
CHKFORTRANNULLOBJECT(dm);
PetscBool ids_null = !*(void**) ids ? PETSC_TRUE : PETSC_FALSE;
CHKFORTRANNULLOBJECT(ids);
/* insert Fortran-to-C conversion for name */
  FIXCHAR(name,cl0,_cltmp0);
*ierr = DMGetLabelIdIS(
	(DM)PetscToPointer((dm) ),_cltmp0,ids);
  FREECHAR(name,_cltmp0);
// if C routine nullifed the object, we must set to to -2 to indicate null set in Fortran
if (! ids_null && !*(void**) ids) * (void **) ids = (void *)-2;
}
PETSC_EXTERN void  dmgetstratumsize_(DM dm, char name[],PetscInt *value,PetscInt *size, int *ierr, PETSC_FORTRAN_CHARLEN_T cl0)
{
  char *_cltmp0 = PETSC_NULLPTR;
CHKFORTRANNULLOBJECT(dm);
CHKFORTRANNULLINTEGER(size);
/* insert Fortran-to-C conversion for name */
  FIXCHAR(name,cl0,_cltmp0);
*ierr = DMGetStratumSize(
	(DM)PetscToPointer((dm) ),_cltmp0,*value,size);
  FREECHAR(name,_cltmp0);
}
PETSC_EXTERN void  dmgetstratumis_(DM dm, char name[],PetscInt *value,IS *points, int *ierr, PETSC_FORTRAN_CHARLEN_T cl0)
{
  char *_cltmp0 = PETSC_NULLPTR;
CHKFORTRANNULLOBJECT(dm);
PetscBool points_null = !*(void**) points ? PETSC_TRUE : PETSC_FALSE;
CHKFORTRANNULLOBJECT(points);
/* insert Fortran-to-C conversion for name */
  FIXCHAR(name,cl0,_cltmp0);
*ierr = DMGetStratumIS(
	(DM)PetscToPointer((dm) ),_cltmp0,*value,points);
  FREECHAR(name,_cltmp0);
// if C routine nullifed the object, we must set to to -2 to indicate null set in Fortran
if (! points_null && !*(void**) points) * (void **) points = (void *)-2;
}
PETSC_EXTERN void  dmsetstratumis_(DM dm, char name[],PetscInt *value,IS points, int *ierr, PETSC_FORTRAN_CHARLEN_T cl0)
{
  char *_cltmp0 = PETSC_NULLPTR;
CHKFORTRANNULLOBJECT(dm);
CHKFORTRANNULLOBJECT(points);
/* insert Fortran-to-C conversion for name */
  FIXCHAR(name,cl0,_cltmp0);
*ierr = DMSetStratumIS(
	(DM)PetscToPointer((dm) ),_cltmp0,*value,
	(IS)PetscToPointer((points) ));
  FREECHAR(name,_cltmp0);
}
PETSC_EXTERN void  dmclearlabelstratum_(DM dm, char name[],PetscInt *value, int *ierr, PETSC_FORTRAN_CHARLEN_T cl0)
{
  char *_cltmp0 = PETSC_NULLPTR;
CHKFORTRANNULLOBJECT(dm);
/* insert Fortran-to-C conversion for name */
  FIXCHAR(name,cl0,_cltmp0);
*ierr = DMClearLabelStratum(
	(DM)PetscToPointer((dm) ),_cltmp0,*value);
  FREECHAR(name,_cltmp0);
}
PETSC_EXTERN void  dmgetnumlabels_(DM dm,PetscInt *numLabels, int *ierr)
{
CHKFORTRANNULLOBJECT(dm);
CHKFORTRANNULLINTEGER(numLabels);
*ierr = DMGetNumLabels(
	(DM)PetscToPointer((dm) ),numLabels);
}
PETSC_EXTERN void  dmgetlabelname_(DM dm,PetscInt *n, char *name, int *ierr, PETSC_FORTRAN_CHARLEN_T cl0)
{
  char *_cltmp0 = PETSC_NULLPTR;
CHKFORTRANNULLOBJECT(dm);
*ierr = DMGetLabelName(
	(DM)PetscToPointer((dm) ),*n,(const char **)&_cltmp0);
/* insert C-to-Fortran conversion for name */
*ierr = PetscStrncpy(name, _cltmp0, cl0);
                        if (*ierr) return;
                        FIXRETURNCHAR(PETSC_TRUE, name, cl0);
}
PETSC_EXTERN void  dmhaslabel_(DM dm, char name[],PetscBool *hasLabel, int *ierr, PETSC_FORTRAN_CHARLEN_T cl0)
{
  char *_cltmp0 = PETSC_NULLPTR;
CHKFORTRANNULLOBJECT(dm);
/* insert Fortran-to-C conversion for name */
  FIXCHAR(name,cl0,_cltmp0);
*ierr = DMHasLabel(
	(DM)PetscToPointer((dm) ),_cltmp0,hasLabel);
  FREECHAR(name,_cltmp0);
}
PETSC_EXTERN void  dmgetlabel_(DM dm, char name[],DMLabel *label, int *ierr, PETSC_FORTRAN_CHARLEN_T cl0)
{
  char *_cltmp0 = PETSC_NULLPTR;
CHKFORTRANNULLOBJECT(dm);
PetscBool label_null = !*(void**) label ? PETSC_TRUE : PETSC_FALSE;
CHKFORTRANNULLOBJECT(label);
/* insert Fortran-to-C conversion for name */
  FIXCHAR(name,cl0,_cltmp0);
*ierr = DMGetLabel(
	(DM)PetscToPointer((dm) ),_cltmp0,label);
  FREECHAR(name,_cltmp0);
// if C routine nullifed the object, we must set to to -2 to indicate null set in Fortran
if (! label_null && !*(void**) label) * (void **) label = (void *)-2;
}
PETSC_EXTERN void  dmgetlabelbynum_(DM dm,PetscInt *n,DMLabel *label, int *ierr)
{
CHKFORTRANNULLOBJECT(dm);
PetscBool label_null = !*(void**) label ? PETSC_TRUE : PETSC_FALSE;
CHKFORTRANNULLOBJECT(label);
*ierr = DMGetLabelByNum(
	(DM)PetscToPointer((dm) ),*n,label);
// if C routine nullifed the object, we must set to to -2 to indicate null set in Fortran
if (! label_null && !*(void**) label) * (void **) label = (void *)-2;
}
PETSC_EXTERN void  dmaddlabel_(DM dm,DMLabel label, int *ierr)
{
CHKFORTRANNULLOBJECT(dm);
CHKFORTRANNULLOBJECT(label);
*ierr = DMAddLabel(
	(DM)PetscToPointer((dm) ),
	(DMLabel)PetscToPointer((label) ));
}
PETSC_EXTERN void  dmsetlabel_(DM dm,DMLabel label, int *ierr)
{
CHKFORTRANNULLOBJECT(dm);
CHKFORTRANNULLOBJECT(label);
*ierr = DMSetLabel(
	(DM)PetscToPointer((dm) ),
	(DMLabel)PetscToPointer((label) ));
}
PETSC_EXTERN void  dmremovelabel_(DM dm, char name[],DMLabel *label, int *ierr, PETSC_FORTRAN_CHARLEN_T cl0)
{
  char *_cltmp0 = PETSC_NULLPTR;
CHKFORTRANNULLOBJECT(dm);
PetscBool label_null = !*(void**) label ? PETSC_TRUE : PETSC_FALSE;
CHKFORTRANNULLOBJECT(label);
/* insert Fortran-to-C conversion for name */
  FIXCHAR(name,cl0,_cltmp0);
*ierr = DMRemoveLabel(
	(DM)PetscToPointer((dm) ),_cltmp0,label);
  FREECHAR(name,_cltmp0);
// if C routine nullifed the object, we must set to to -2 to indicate null set in Fortran
if (! label_null && !*(void**) label) * (void **) label = (void *)-2;
}
PETSC_EXTERN void  dmremovelabelbyself_(DM dm,DMLabel *label,PetscBool *failNotFound, int *ierr)
{
CHKFORTRANNULLOBJECT(dm);
PetscBool label_null = !*(void**) label ? PETSC_TRUE : PETSC_FALSE;
CHKFORTRANNULLOBJECT(label);
*ierr = DMRemoveLabelBySelf(
	(DM)PetscToPointer((dm) ),label,*failNotFound);
// if C routine nullifed the object, we must set to to -2 to indicate null set in Fortran
if (! label_null && !*(void**) label) * (void **) label = (void *)-2;
}
PETSC_EXTERN void  dmgetlabeloutput_(DM dm, char name[],PetscBool *output, int *ierr, PETSC_FORTRAN_CHARLEN_T cl0)
{
  char *_cltmp0 = PETSC_NULLPTR;
CHKFORTRANNULLOBJECT(dm);
/* insert Fortran-to-C conversion for name */
  FIXCHAR(name,cl0,_cltmp0);
*ierr = DMGetLabelOutput(
	(DM)PetscToPointer((dm) ),_cltmp0,output);
  FREECHAR(name,_cltmp0);
}
PETSC_EXTERN void  dmsetlabeloutput_(DM dm, char name[],PetscBool *output, int *ierr, PETSC_FORTRAN_CHARLEN_T cl0)
{
  char *_cltmp0 = PETSC_NULLPTR;
CHKFORTRANNULLOBJECT(dm);
/* insert Fortran-to-C conversion for name */
  FIXCHAR(name,cl0,_cltmp0);
*ierr = DMSetLabelOutput(
	(DM)PetscToPointer((dm) ),_cltmp0,*output);
  FREECHAR(name,_cltmp0);
}
PETSC_EXTERN void  dmcopylabels_(DM dmA,DM dmB,PetscCopyMode *mode,PetscBool *all,DMCopyLabelsMode *emode, int *ierr)
{
CHKFORTRANNULLOBJECT(dmA);
CHKFORTRANNULLOBJECT(dmB);
*ierr = DMCopyLabels(
	(DM)PetscToPointer((dmA) ),
	(DM)PetscToPointer((dmB) ),*mode,*all,*emode);
}
PETSC_EXTERN void  dmgetcoarsedm_(DM dm,DM *cdm, int *ierr)
{
CHKFORTRANNULLOBJECT(dm);
PetscBool cdm_null = !*(void**) cdm ? PETSC_TRUE : PETSC_FALSE;
CHKFORTRANNULLOBJECT(cdm);
*ierr = DMGetCoarseDM(
	(DM)PetscToPointer((dm) ),cdm);
// if C routine nullifed the object, we must set to to -2 to indicate null set in Fortran
if (! cdm_null && !*(void**) cdm) * (void **) cdm = (void *)-2;
}
PETSC_EXTERN void  dmsetcoarsedm_(DM dm,DM cdm, int *ierr)
{
CHKFORTRANNULLOBJECT(dm);
CHKFORTRANNULLOBJECT(cdm);
*ierr = DMSetCoarseDM(
	(DM)PetscToPointer((dm) ),
	(DM)PetscToPointer((cdm) ));
}
PETSC_EXTERN void  dmgetfinedm_(DM dm,DM *fdm, int *ierr)
{
CHKFORTRANNULLOBJECT(dm);
PetscBool fdm_null = !*(void**) fdm ? PETSC_TRUE : PETSC_FALSE;
CHKFORTRANNULLOBJECT(fdm);
*ierr = DMGetFineDM(
	(DM)PetscToPointer((dm) ),fdm);
// if C routine nullifed the object, we must set to to -2 to indicate null set in Fortran
if (! fdm_null && !*(void**) fdm) * (void **) fdm = (void *)-2;
}
PETSC_EXTERN void  dmsetfinedm_(DM dm,DM fdm, int *ierr)
{
CHKFORTRANNULLOBJECT(dm);
CHKFORTRANNULLOBJECT(fdm);
*ierr = DMSetFineDM(
	(DM)PetscToPointer((dm) ),
	(DM)PetscToPointer((fdm) ));
}
PETSC_EXTERN void  matfdcoloringusedm_(Mat coloring,MatFDColoring fdcoloring, int *ierr)
{
CHKFORTRANNULLOBJECT(coloring);
CHKFORTRANNULLOBJECT(fdcoloring);
*ierr = MatFDColoringUseDM(
	(Mat)PetscToPointer((coloring) ),
	(MatFDColoring)PetscToPointer((fdcoloring) ));
}
PETSC_EXTERN void  dmgetcompatibility_(DM dm1,DM dm2,PetscBool *compatible,PetscBool *set, int *ierr)
{
CHKFORTRANNULLOBJECT(dm1);
CHKFORTRANNULLOBJECT(dm2);
*ierr = DMGetCompatibility(
	(DM)PetscToPointer((dm1) ),
	(DM)PetscToPointer((dm2) ),compatible,set);
}
PETSC_EXTERN void  dmmonitorcancel_(DM dm, int *ierr)
{
CHKFORTRANNULLOBJECT(dm);
*ierr = DMMonitorCancel(
	(DM)PetscToPointer((dm) ));
}
PETSC_EXTERN void  dmmonitor_(DM dm, int *ierr)
{
CHKFORTRANNULLOBJECT(dm);
*ierr = DMMonitor(
	(DM)PetscToPointer((dm) ));
}
PETSC_EXTERN void  dmcomputeerror_(DM dm,Vec sol,PetscReal errors[],Vec *errorVec, int *ierr)
{
CHKFORTRANNULLOBJECT(dm);
CHKFORTRANNULLOBJECT(sol);
CHKFORTRANNULLREAL(errors);
PetscBool errorVec_null = !*(void**) errorVec ? PETSC_TRUE : PETSC_FALSE;
CHKFORTRANNULLOBJECT(errorVec);
*ierr = DMComputeError(
	(DM)PetscToPointer((dm) ),
	(Vec)PetscToPointer((sol) ),errors,errorVec);
// if C routine nullifed the object, we must set to to -2 to indicate null set in Fortran
if (! errorVec_null && !*(void**) errorVec) * (void **) errorVec = (void *)-2;
}
PETSC_EXTERN void  dmgetnumauxiliaryvec_(DM dm,PetscInt *numAux, int *ierr)
{
CHKFORTRANNULLOBJECT(dm);
CHKFORTRANNULLINTEGER(numAux);
*ierr = DMGetNumAuxiliaryVec(
	(DM)PetscToPointer((dm) ),numAux);
}
PETSC_EXTERN void  dmgetauxiliaryvec_(DM dm,DMLabel label,PetscInt *value,PetscInt *part,Vec *aux, int *ierr)
{
CHKFORTRANNULLOBJECT(dm);
CHKFORTRANNULLOBJECT(label);
PetscBool aux_null = !*(void**) aux ? PETSC_TRUE : PETSC_FALSE;
CHKFORTRANNULLOBJECT(aux);
*ierr = DMGetAuxiliaryVec(
	(DM)PetscToPointer((dm) ),
	(DMLabel)PetscToPointer((label) ),*value,*part,aux);
// if C routine nullifed the object, we must set to to -2 to indicate null set in Fortran
if (! aux_null && !*(void**) aux) * (void **) aux = (void *)-2;
}
PETSC_EXTERN void  dmsetauxiliaryvec_(DM dm,DMLabel label,PetscInt *value,PetscInt *part,Vec aux, int *ierr)
{
CHKFORTRANNULLOBJECT(dm);
CHKFORTRANNULLOBJECT(label);
CHKFORTRANNULLOBJECT(aux);
*ierr = DMSetAuxiliaryVec(
	(DM)PetscToPointer((dm) ),
	(DMLabel)PetscToPointer((label) ),*value,*part,
	(Vec)PetscToPointer((aux) ));
}
PETSC_EXTERN void  dmgetauxiliarylabels_(DM dm,DMLabel labels[],PetscInt values[],PetscInt parts[], int *ierr)
{
CHKFORTRANNULLOBJECT(dm);
PetscBool labels_null = !*(void**) labels ? PETSC_TRUE : PETSC_FALSE;
CHKFORTRANNULLOBJECT(labels);
CHKFORTRANNULLINTEGER(values);
CHKFORTRANNULLINTEGER(parts);
*ierr = DMGetAuxiliaryLabels(
	(DM)PetscToPointer((dm) ),labels,values,parts);
// if C routine nullifed the object, we must set to to -2 to indicate null set in Fortran
if (! labels_null && !*(void**) labels) * (void **) labels = (void *)-2;
}
PETSC_EXTERN void  dmcopyauxiliaryvec_(DM dm,DM dmNew, int *ierr)
{
CHKFORTRANNULLOBJECT(dm);
CHKFORTRANNULLOBJECT(dmNew);
*ierr = DMCopyAuxiliaryVec(
	(DM)PetscToPointer((dm) ),
	(DM)PetscToPointer((dmNew) ));
}
PETSC_EXTERN void  dmclearauxiliaryvec_(DM dm, int *ierr)
{
CHKFORTRANNULLOBJECT(dm);
*ierr = DMClearAuxiliaryVec(
	(DM)PetscToPointer((dm) ));
}
PETSC_EXTERN void  dmpolytopematchorientation_(DMPolytopeType *ct, PetscInt sourceCone[], PetscInt targetCone[],PetscInt *ornt,PetscBool *found, int *ierr)
{
CHKFORTRANNULLINTEGER(sourceCone);
CHKFORTRANNULLINTEGER(targetCone);
CHKFORTRANNULLINTEGER(ornt);
*ierr = DMPolytopeMatchOrientation(*ct,sourceCone,targetCone,ornt,found);
}
PETSC_EXTERN void  dmpolytopegetorientation_(DMPolytopeType *ct, PetscInt sourceCone[], PetscInt targetCone[],PetscInt *ornt, int *ierr)
{
CHKFORTRANNULLINTEGER(sourceCone);
CHKFORTRANNULLINTEGER(targetCone);
CHKFORTRANNULLINTEGER(ornt);
*ierr = DMPolytopeGetOrientation(*ct,sourceCone,targetCone,ornt);
}
PETSC_EXTERN void  dmpolytopematchvertexorientation_(DMPolytopeType *ct, PetscInt sourceVert[], PetscInt targetVert[],PetscInt *ornt,PetscBool *found, int *ierr)
{
CHKFORTRANNULLINTEGER(sourceVert);
CHKFORTRANNULLINTEGER(targetVert);
CHKFORTRANNULLINTEGER(ornt);
*ierr = DMPolytopeMatchVertexOrientation(*ct,sourceVert,targetVert,ornt,found);
}
PETSC_EXTERN void  dmpolytopegetvertexorientation_(DMPolytopeType *ct, PetscInt sourceCone[], PetscInt targetCone[],PetscInt *ornt, int *ierr)
{
CHKFORTRANNULLINTEGER(sourceCone);
CHKFORTRANNULLINTEGER(targetCone);
CHKFORTRANNULLINTEGER(ornt);
*ierr = DMPolytopeGetVertexOrientation(*ct,sourceCone,targetCone,ornt);
}
PETSC_EXTERN void  dmpolytopeincelltest_(DMPolytopeType *ct, PetscReal point[],PetscBool *inside, int *ierr)
{
CHKFORTRANNULLREAL(point);
*ierr = DMPolytopeInCellTest(*ct,point,inside);
}
PETSC_EXTERN void  dmreordersectionsetdefault_(DM dm,DMReorderDefaultFlag *reorder, int *ierr)
{
CHKFORTRANNULLOBJECT(dm);
*ierr = DMReorderSectionSetDefault(
	(DM)PetscToPointer((dm) ),*reorder);
}
PETSC_EXTERN void  dmreordersectiongetdefault_(DM dm,DMReorderDefaultFlag *reorder, int *ierr)
{
CHKFORTRANNULLOBJECT(dm);
*ierr = DMReorderSectionGetDefault(
	(DM)PetscToPointer((dm) ),reorder);
}
PETSC_EXTERN void  dmreordersectionsettype_(DM dm,char *reorder, int *ierr, PETSC_FORTRAN_CHARLEN_T cl0)
{
  char *_cltmp0 = PETSC_NULLPTR;
CHKFORTRANNULLOBJECT(dm);
/* insert Fortran-to-C conversion for reorder */
  FIXCHAR(reorder,cl0,_cltmp0);
*ierr = DMReorderSectionSetType(
	(DM)PetscToPointer((dm) ),_cltmp0);
  FREECHAR(reorder,_cltmp0);
}
PETSC_EXTERN void  dmreordersectiongettype_(DM dm,char *reorder, int *ierr, PETSC_FORTRAN_CHARLEN_T cl0)
{
  char *_cltmp0 = PETSC_NULLPTR;
CHKFORTRANNULLOBJECT(dm);
*ierr = DMReorderSectionGetType(
	(DM)PetscToPointer((dm) ),(const char **)&_cltmp0);
/* insert C-to-Fortran conversion for reorder */
*ierr = PetscStrncpy(reorder, _cltmp0, cl0);
                        if (*ierr) return;
                        FIXRETURNCHAR(PETSC_TRUE, reorder, cl0);
}
#if defined(__cplusplus)
}
#endif
